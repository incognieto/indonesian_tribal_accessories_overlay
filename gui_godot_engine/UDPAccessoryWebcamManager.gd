extends Node
class_name UDPAccessoryWebcamManager

# Sinyal untuk komunikasi dengan UI
signal frame_received(texture: ImageTexture)
signal connection_changed(connected: bool) 
signal error_message(message: String)

var udp_socket: PacketPeerUDP
var webcam_connected: bool = false
var server_host: String = "127.0.0.1"
var server_port: int = 8888  # UDP port (same as udp_webcam_server.py)

# Buffer untuk menyimpan data yang diterima
var receive_buffer: PackedByteArray = PackedByteArray()
var packet_sequence: int = 0
var total_packets: int = 0
var received_packets: Dictionary = {}
var current_frame_id: int = -1

# Statistics
var frames_received: int = 0
var last_fps_time: float = 0.0
var current_fps: float = 0.0
var packets_lost: int = 0
var total_packets_received: int = 0

# UDP Configuration
const MAX_PACKET_SIZE = 60000  # Maximum UDP packet payload
const FRAME_TIMEOUT = 2.0  # Detik untuk timeout frame incomplete
var frame_timeout_timer: float = 0.0

func _ready():
	"""Inisialisasi saat node ready"""
	print("=== UDPAccessoryWebcamManager initialized ===")
	set_process(false)  # Disabled sampai connect dipanggil

func connect_to_webcam_server():
	"""Koneksi ke UDP webcam overlay server"""
	if webcam_connected:
		print("Already connected to webcam server")
		return
	
	udp_socket = PacketPeerUDP.new()
	
	# Bind ke port arbitrary untuk menerima data (0 = sistem pilih port)
	var result = udp_socket.bind(0)  # Bind ke port random
	
	if result == OK:
		# Set target server
		udp_socket.set_dest_address(server_host, server_port)
		
		# Kirim REGISTER message ke server
		var register_msg = "REGISTER".to_utf8_buffer()
		udp_socket.put_packet(register_msg)
		
		print("✅ UDP socket bound, sent REGISTER to %s:%d" % [server_host, server_port])
		print("🔧 Enabling _process() for packet polling...")
		webcam_connected = true
		connection_changed.emit(true)
		set_process(true)
	else:
		print("❌ Failed to bind UDP socket: %d" % result)
		error_message.emit("Failed to bind UDP socket")

func _process(delta):
	"""Process dipanggil setiap frame untuk menerima data"""
	if not udp_socket or not webcam_connected:
		return
	
	# Update frame timeout
	if current_frame_id >= 0:
		frame_timeout_timer += delta
		if frame_timeout_timer > FRAME_TIMEOUT:
			print("⏰ Frame %d timeout - discarding incomplete frame" % current_frame_id)
			_reset_frame_buffer()
	
	# Baca semua paket yang tersedia
	while udp_socket.get_available_packet_count() > 0:
		var packet = udp_socket.get_packet()
		if packet.size() > 0:
			_process_packet(packet)

func _process_packet(packet: PackedByteArray):
	"""Proses paket UDP yang diterima"""
	total_packets_received += 1
	
	# Struktur paket dari udp_webcam_server.py:
	# [0-3]: Sequence number (4 bytes, uint32 big-endian)
	# [4-7]: Total packets (4 bytes, uint32 big-endian)
	# [8-11]: Packet index (4 bytes, uint32 big-endian)
	# [12...]: JPEG data chunk
	
	if packet.size() < 12:
		print("❌ Invalid packet size: %d bytes" % packet.size())
		return
	
	# Parse header (big-endian format sesuai struct.pack("!III"))
	var sequence_num = _bytes_to_uint32(packet.slice(0, 4))
	var total_pkts = _bytes_to_uint32(packet.slice(4, 8))
	var packet_idx = _bytes_to_uint32(packet.slice(8, 12))
	
	# Data payload
	var payload = packet.slice(12)
	
	# Debug info (setiap 30 paket)
	if total_packets_received % 30 == 0:
		print("📦 Packet: Seq=%d, Idx=%d/%d, Size=%d bytes" % [sequence_num, packet_idx, total_pkts, payload.size()])
	
	# Jika frame baru (sequence number berbeda)
	if sequence_num != current_frame_id:
		if current_frame_id >= 0:
			# Frame sebelumnya belum lengkap
			var missing = total_packets - received_packets.size()
			if missing > 0:
				print("⚠️ Frame %d incomplete: missing %d packets" % [current_frame_id, missing])
				packets_lost += missing
		
		# Reset untuk frame baru
		_reset_frame_buffer()
		current_frame_id = sequence_num
		total_packets = total_pkts
		frame_timeout_timer = 0.0
		
		print("🆕 New frame: Seq=%d, Total packets=%d" % [sequence_num, total_pkts])
	
	# Simpan paket berdasarkan index
	if packet_idx not in received_packets:
		received_packets[packet_idx] = payload
	
	# Cek apakah frame lengkap
	if received_packets.size() == total_packets:
		print("✅ Frame %d complete: %d packets received" % [sequence_num, total_packets])
		_assemble_and_process_frame()

func _assemble_and_process_frame():
	"""Gabungkan semua paket menjadi satu frame dan proses"""
	# Gabungkan paket sesuai urutan
	var frame_data = PackedByteArray()
	
	for i in range(total_packets):
		if i in received_packets:
			frame_data.append_array(received_packets[i])
		else:
			print("❌ Missing packet %d in frame assembly!" % i)
			_reset_frame_buffer()
			return
	
	print("🖼️ Assembled frame: %d bytes from %d packets" % [frame_data.size(), total_packets])
	
	# Decode JPEG
	if frame_data.size() > 0:
		var image = Image.new()
		var load_error = image.load_jpg_from_buffer(frame_data)
		
		if load_error == OK:
			var texture = ImageTexture.new()
			texture.set_image(image)
			print("✅ Emitting frame signal (size: %dx%d)" % [image.get_width(), image.get_height()])
			frame_received.emit(texture)
			
			# Update statistics
			frames_received += 1
			_update_fps()
		else:
			print("❌ JPEG decode error: %d" % load_error)
			error_message.emit("Failed to decode frame")
	
	# Reset untuk frame berikutnya
	_reset_frame_buffer()

func _reset_frame_buffer():
	"""Reset buffer untuk frame baru"""
	received_packets.clear()
	current_frame_id = -1
	total_packets = 0
	frame_timeout_timer = 0.0

func _bytes_to_uint32(bytes: PackedByteArray) -> int:
	"""Convert 4 bytes to uint32 (big endian / network byte order)"""
	return (bytes[0] << 24) | (bytes[1] << 16) | (bytes[2] << 8) | bytes[3]

func _update_fps():
	"""Update FPS counter"""
	var current_time = Time.get_ticks_msec() / 1000.0
	
	if last_fps_time == 0.0:
		last_fps_time = current_time
		return
	
	var elapsed = current_time - last_fps_time
	
	if elapsed >= 1.0:
		current_fps = frames_received / elapsed
		frames_received = 0
		last_fps_time = current_time
		
		# Print statistics
		if total_packets_received % 100 == 0:
			print("📊 Stats: FPS=%.1f, Packets lost=%d, Total received=%d" % [current_fps, packets_lost, total_packets_received])

func disconnect_from_server():
	"""Putuskan koneksi dari server"""
	if udp_socket:
		# Kirim UNREGISTER message
		var unregister_msg = "UNREGISTER".to_utf8_buffer()
		udp_socket.put_packet(unregister_msg)
		
		udp_socket.close()
		udp_socket = null
	
	webcam_connected = false
	connection_changed.emit(false)
	set_process(false)
	
	# Reset buffers
	_reset_frame_buffer()
	
	print("Disconnected from UDP webcam server")

func get_connection_status() -> bool:
	"""Cek status koneksi"""
	return webcam_connected

func get_fps() -> float:
	"""Get current FPS"""
	return current_fps

func get_packet_loss() -> int:
	"""Get total packets lost"""
	return packets_lost

func send_command(command: String):
	"""Send command to server (e.g., package switch)"""
	if not udp_socket or not webcam_connected:
		print("Cannot send command: not connected")
		return
	
	var command_msg = command.to_utf8_buffer()
	var result = udp_socket.put_packet(command_msg)
	
	if result == OK:
		print("✉️ Command sent: %s" % command)
	else:
		print("❌ Failed to send command: %s" % command)

func send_package_switch(package_id: int):
	"""Send package switch command to server"""
	var command = "PACKAGE:%d" % package_id
	send_command(command)
	print("📦 Package switch requested: %d" % package_id)

func send_cascade_change(cascade_file: String):
	"""Send cascade change command to server"""
	var command = "CASCADE:%s" % cascade_file
	send_command(command)
	print("🔄 Cascade change requested: %s" % cascade_file)

func send_settings_update(settings: Dictionary):
	"""Send settings update to server"""
	if not udp_socket or not webcam_connected:
		print("Cannot send settings: not connected")
		return
	
	# Convert settings dictionary to JSON
	var settings_json = JSON.stringify(settings)
	var command = "SETTINGS:" + settings_json
	
	print("⚙️ Sending settings:", settings_json)
	send_command(command)

func _notification(what):
	"""Handle notification events"""
	if what == NOTIFICATION_WM_CLOSE_REQUEST or what == NOTIFICATION_PREDELETE:
		disconnect_from_server()
