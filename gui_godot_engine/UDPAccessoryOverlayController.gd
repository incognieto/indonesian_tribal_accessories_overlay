extends Control

# UI Node References (FREE POSITIONING - No Containers)
@onready var webcam_feed = $WebcamPanel/WebcamFeed
@onready var status_label = $WebcamPanel/WebcamFeed/StatusLabel
@onready var fps_label = $WebcamPanel/WebcamFeed/FPSLabel
@onready var title_label = $TitleLabel
@onready var subtitle_label = $SubtitleLabel
@onready var connect_button = $ButtonsPanel/ConnectButton
@onready var disconnect_button = $ButtonsPanel/DisconnectButton
@onready var info_label = $InfoLabel
@onready var stats_label = $WebcamPanel/WebcamFeed/StatsLabel
@onready var back_button = $BackButton
@onready var settings_button = $SettingsButton

# Settings Panel
@onready var settings_panel = $AccessorySettingsPanel
@onready var settings_apply_button = $AccessorySettingsPanel/VBoxContainer/ButtonsContainer/ApplyButton
@onready var settings_reset_button = $AccessorySettingsPanel/VBoxContainer/ButtonsContainer/ResetButton
@onready var settings_close_button = $AccessorySettingsPanel/VBoxContainer/CloseButton

# Cascade Selection
@onready var cascade_option_button = $AccessorySettingsPanel/VBoxContainer/ScrollContainer/SettingsContent/CascadeSection/CascadeOptionButton
@onready var cascade_desc_label = $AccessorySettingsPanel/VBoxContainer/ScrollContainer/SettingsContent/CascadeSection/CascadeDesc

# Settings Sliders - HAT
@onready var hat_scale_slider = $AccessorySettingsPanel/VBoxContainer/ScrollContainer/SettingsContent/HatSection/HatScaleSlider
@onready var hat_scale_value = $AccessorySettingsPanel/VBoxContainer/ScrollContainer/SettingsContent/HatSection/HatScaleContainer/HatScaleValue
@onready var hat_y_offset_slider = $AccessorySettingsPanel/VBoxContainer/ScrollContainer/SettingsContent/HatSection/HatYOffsetSlider
@onready var hat_y_offset_value = $AccessorySettingsPanel/VBoxContainer/ScrollContainer/SettingsContent/HatSection/HatYOffsetContainer/HatYOffsetValue

# Settings Sliders - EARRING
@onready var earring_scale_slider = $AccessorySettingsPanel/VBoxContainer/ScrollContainer/SettingsContent/EarringSection/EarringScaleSlider
@onready var earring_scale_value = $AccessorySettingsPanel/VBoxContainer/ScrollContainer/SettingsContent/EarringSection/EarringScaleContainer/EarringScaleValue
@onready var earring_y_offset_slider = $AccessorySettingsPanel/VBoxContainer/ScrollContainer/SettingsContent/EarringSection/EarringYOffsetSlider
@onready var earring_y_offset_value = $AccessorySettingsPanel/VBoxContainer/ScrollContainer/SettingsContent/EarringSection/EarringYOffsetContainer/EarringYOffsetValue

# Settings Sliders - PIERCING
@onready var piercing_scale_slider = $AccessorySettingsPanel/VBoxContainer/ScrollContainer/SettingsContent/PiercingSection/PiercingScaleSlider
@onready var piercing_scale_value = $AccessorySettingsPanel/VBoxContainer/ScrollContainer/SettingsContent/PiercingSection/PiercingScaleContainer/PiercingScaleValue
@onready var piercing_y_offset_slider = $AccessorySettingsPanel/VBoxContainer/ScrollContainer/SettingsContent/PiercingSection/PiercingYOffsetSlider
@onready var piercing_y_offset_value = $AccessorySettingsPanel/VBoxContainer/ScrollContainer/SettingsContent/PiercingSection/PiercingYOffsetContainer/PiercingYOffsetValue

# Debug Options - use get_node_or_null to avoid error if not found
var bounding_box_checkbox: CheckBox

# Package buttons (static nodes - free positioning)
@onready var package1_button = $PackagePanel/Package1Button
@onready var package2_button = $PackagePanel/Package2Button
@onready var package3_button = $PackagePanel/Package3Button
@onready var package4_button = $PackagePanel/Package4Button
@onready var package5_button = $PackagePanel/Package5Button

# Webcam Manager
var webcam_manager: Node
var fps_update_timer: Timer
var current_package: int = 1

func _ready():
	"""Inisialisasi UI dan webcam manager"""
	print("=== UDPAccessoryOverlayController._ready() ===")
	
	# Initialize bounding box checkbox reference
	bounding_box_checkbox = get_node_or_null("AccessorySettingsPanel/VBoxContainer/ScrollContainer/SettingsContent/DebugSection/BoundingBoxContainer/BoundingBoxCheckBox")
	if not bounding_box_checkbox:
		print("⚠️ Warning: BoundingBoxCheckBox not found in scene")
	
	setup_ui()
	setup_webcam_manager()
	setup_fps_timer()
	connect_package_buttons()
	connect_settings_controls()
	
	print("UDP Controller initialized successfully")

func setup_ui():
	"""Setup UI elements"""
	# Setup placeholder webcam
	setup_webcam_placeholder()
	
	# Setup title untuk UDP version
	if title_label:
		title_label.text = "Accessory Overlay System (UDP)"
	if subtitle_label:
		subtitle_label.text = "Real-time Face Detection & Overlay via UDP Stream"
	
	# Setup buttons (check if not already connected to avoid duplicates)
	if not connect_button.pressed.is_connected(_on_connect_pressed):
		connect_button.pressed.connect(_on_connect_pressed)
	if not disconnect_button.pressed.is_connected(_on_disconnect_pressed):
		disconnect_button.pressed.connect(_on_disconnect_pressed)
	disconnect_button.disabled = true
	if not back_button.pressed.is_connected(_on_back_pressed):
		back_button.pressed.connect(_on_back_pressed)
	if not settings_button.pressed.is_connected(_on_settings_pressed):
		settings_button.pressed.connect(_on_settings_pressed)
	
	# Setup initial status
	status_label.text = "Klik 'Connect' untuk memulai (UDP Mode)"
	status_label.modulate = Color(1, 1, 1, 0.9)
	fps_label.text = "FPS: --"
	fps_label.modulate = Color(0, 1, 0, 0.9)
	
	# Setup stats label if exists
	if stats_label:
		stats_label.text = ""
		stats_label.modulate = Color(0.8, 0.8, 1, 0.9)
	
	# Setup info
	info_label.text = "Sistem Overlay Aksesoris menggunakan UDP untuk streaming cepat"
	
	print("UI setup complete (UDP mode)")

func setup_webcam_placeholder():
	"""Buat placeholder image untuk webcam"""
	var placeholder_image = Image.create(640, 480, false, Image.FORMAT_RGBA8)
	placeholder_image.fill(Color(0.15, 0.15, 0.2, 1.0))
	
	# Draw border
	for x in range(640):
		for y in range(8):
			placeholder_image.set_pixel(x, y, Color(0.3, 0.3, 0.4, 1.0))
			placeholder_image.set_pixel(x, 479-y, Color(0.3, 0.3, 0.4, 1.0))
	
	for y in range(480):
		for x in range(8):
			placeholder_image.set_pixel(x, y, Color(0.3, 0.3, 0.4, 1.0))
			placeholder_image.set_pixel(639-x, y, Color(0.3, 0.3, 0.4, 1.0))
	
	# Draw "UDP" text in center (simple)
	var center_y = 240
	var text_color = Color(0.5, 0.5, 0.6, 1.0)
	for x in range(280, 360):
		for y in range(center_y - 10, center_y + 10):
			if (x + y) % 3 == 0:  # Simple pattern
				placeholder_image.set_pixel(x, y, text_color)
	
	var placeholder_texture = ImageTexture.new()
	placeholder_texture.set_image(placeholder_image)
	webcam_feed.texture = placeholder_texture

func setup_webcam_manager():
	"""Setup webcam manager untuk menerima stream UDP"""
	print("=== Setting up UDPAccessoryWebcamManager ===")
	
	# Verifikasi node webcam_feed
	if not webcam_feed:
		print("ERROR: webcam_feed node not found!")
		return
	
	# Load UDPAccessoryWebcamManager script
	var webcam_script = load("res://UDPAccessoryWebcamManager.gd")
	if webcam_script == null:
		print("❌ Error: Could not load UDPAccessoryWebcamManager.gd")
		status_label.text = "Error: UDPAccessoryWebcamManager tidak ditemukan"
		status_label.modulate = Color(1, 0, 0, 0.8)
		return
	
	print("Creating UDPAccessoryWebcamManager instance...")
	webcam_manager = webcam_script.new()
	add_child(webcam_manager)
	
	# Connect signals
	if webcam_manager.has_signal("frame_received"):
		webcam_manager.frame_received.connect(_on_webcam_frame_received)
		print("✅ frame_received signal connected")
	
	if webcam_manager.has_signal("connection_changed"):
		webcam_manager.connection_changed.connect(_on_webcam_connection_changed)
		print("✅ connection_changed signal connected")
	
	if webcam_manager.has_signal("error_message"):
		webcam_manager.error_message.connect(_on_webcam_error)
		print("✅ error_message signal connected")
	
	print("UDPAccessoryWebcamManager setup complete")

func setup_fps_timer():
	"""Setup timer untuk update FPS"""
	fps_update_timer = Timer.new()
	fps_update_timer.wait_time = 0.5  # Update setiap 0.5 detik
	fps_update_timer.timeout.connect(_on_fps_timer_timeout)
	add_child(fps_update_timer)
	fps_update_timer.start()

func _on_connect_pressed():
	"""Handler untuk tombol Connect"""
	if webcam_manager and not webcam_manager.get_connection_status():
		print("Connecting to UDP webcam server...")
		status_label.text = "Membuka UDP socket..."
		status_label.modulate = Color(1, 1, 0, 0.9)
		webcam_manager.connect_to_webcam_server()
		
		connect_button.disabled = true
		disconnect_button.disabled = false

func _on_disconnect_pressed():
	"""Handler untuk tombol Disconnect"""
	if webcam_manager and webcam_manager.get_connection_status():
		print("Disconnecting from UDP webcam server...")
		webcam_manager.disconnect_from_server()
		
		status_label.text = "UDP socket ditutup"
		status_label.modulate = Color(1, 0.5, 0, 0.9)
		fps_label.text = "FPS: --"
		
		if stats_label:
			stats_label.text = ""
		
		setup_webcam_placeholder()
		
		connect_button.disabled = false
		disconnect_button.disabled = true

func _on_webcam_frame_received(texture: ImageTexture):
	"""Callback ketika frame webcam diterima"""
	print("🎬 Controller received frame signal (UDP)")  # DEBUG
	if not webcam_feed:
		print("ERROR: webcam_feed node is null!")
		return
	
	# Update texture
	print("🖼️ Updating webcam_feed.texture")  # DEBUG
	webcam_feed.texture = texture

func _on_webcam_connection_changed(connected: bool):
	"""Callback ketika status koneksi webcam berubah"""
	if connected:
		status_label.text = "✅ UDP Socket Terbuka - Menunggu data..."
		status_label.modulate = Color(0, 1, 0, 0.9)
		print("UDP webcam server connected")
		
		# Hide status label after 3 seconds
		var hide_timer = Timer.new()
		hide_timer.wait_time = 3.0
		hide_timer.one_shot = true
		hide_timer.timeout.connect(func(): 
			if status_label:
				status_label.visible = false
			hide_timer.queue_free()
		)
		add_child(hide_timer)
		hide_timer.start()
		
	else:
		status_label.text = "❌ UDP Socket ditutup"
		status_label.modulate = Color(1, 0, 0, 0.9)
		status_label.visible = true
		fps_label.text = "FPS: --"
		
		if stats_label:
			stats_label.text = ""
		
		print("UDP webcam server disconnected")
		
		connect_button.disabled = false
		disconnect_button.disabled = true

func _on_webcam_error(message: String):
	"""Callback ketika terjadi error webcam"""
	status_label.text = "❌ Error: " + message
	status_label.modulate = Color(1, 0, 0, 0.9)
	status_label.visible = true
	print("Webcam Error: " + message)

func _on_fps_timer_timeout():
	"""Update FPS display"""
	if webcam_manager and webcam_manager.get_connection_status():
		var fps = webcam_manager.get_fps()
		if fps > 0:
			fps_label.text = "FPS: %.1f" % fps
		else:
			fps_label.text = "FPS: --"
		
		# Update stats if label exists
		if stats_label and webcam_manager.has_method("get_packet_loss"):
			var packet_loss = webcam_manager.get_packet_loss()
			if packet_loss > 0:
				stats_label.text = "Packet Loss: %d" % packet_loss
			else:
				stats_label.text = "UDP: No packet loss"

func _notification(what):
	"""Handle notification events"""
	if what == NOTIFICATION_WM_CLOSE_REQUEST or what == NOTIFICATION_PREDELETE:
		print("Closing UDP controller...")
		if webcam_manager:
			webcam_manager.disconnect_from_server()

func connect_package_buttons():
	"""Connect package button signals (STATIC VERSION)"""
	print("=== Setting up package buttons (static) ===")
	
	# Connect each button to handler with package ID (check if not already connected)
	if not package1_button.pressed.is_connected(_on_package_pressed):
		package1_button.pressed.connect(_on_package_pressed.bind(1))
	if not package2_button.pressed.is_connected(_on_package_pressed):
		package2_button.pressed.connect(_on_package_pressed.bind(2))
	if not package3_button.pressed.is_connected(_on_package_pressed):
		package3_button.pressed.connect(_on_package_pressed.bind(3))
	if not package4_button.pressed.is_connected(_on_package_pressed):
		package4_button.pressed.connect(_on_package_pressed.bind(4))
	if not package5_button.pressed.is_connected(_on_package_pressed):
		package5_button.pressed.connect(_on_package_pressed.bind(5))
	
	print("✅ 5 package buttons connected successfully")

func _on_package_pressed(package_id: int):
	"""Handle package button press"""
	print("=== Package button %d pressed ===" % package_id)
	
	if not webcam_manager:
		print("ERROR: webcam manager not ready")
		return
	
	if not webcam_manager.get_connection_status():
		print("Cannot switch package: Not connected to server")
		status_label.text = "Connect first before switching package"
		status_label.modulate = Color(1, 0.5, 0, 0.9)
		return
	
	# Update current package
	current_package = package_id
	
	# Send package switch command via UDP
	webcam_manager.send_package_switch(package_id)
	
	# Update UI
	status_label.text = "Switching to Package %d..." % package_id
	status_label.modulate = Color(0.5, 1, 0.5, 0.9)
	
	print("Package switch command sent: %d" % package_id)

func connect_settings_controls():
	"""Connect settings panel controls"""
	print("=== Setting up settings panel controls ===")
	
	# Hide settings panel initially
	if settings_panel:
		settings_panel.visible = false
	
	# Setup cascade options
	setup_cascade_options()
	
	# Connect settings buttons (check if not already connected)
	if settings_close_button and not settings_close_button.pressed.is_connected(_on_settings_close):
		settings_close_button.pressed.connect(_on_settings_close)
	if settings_apply_button and not settings_apply_button.pressed.is_connected(_on_settings_apply):
		settings_apply_button.pressed.connect(_on_settings_apply)
	if settings_reset_button and not settings_reset_button.pressed.is_connected(_on_settings_reset):
		settings_reset_button.pressed.connect(_on_settings_reset)
	
	# Connect cascade option button (check if not already connected)
	if cascade_option_button and not cascade_option_button.item_selected.is_connected(_on_cascade_selected):
		cascade_option_button.item_selected.connect(_on_cascade_selected)
	
	# Connect sliders - HAT (check if not already connected)
	if hat_scale_slider and not hat_scale_slider.value_changed.is_connected(_on_hat_scale_changed):
		hat_scale_slider.value_changed.connect(_on_hat_scale_changed)
	if hat_y_offset_slider and not hat_y_offset_slider.value_changed.is_connected(_on_hat_y_offset_changed):
		hat_y_offset_slider.value_changed.connect(_on_hat_y_offset_changed)
	
	# Connect sliders - EARRING (check if not already connected)
	if earring_scale_slider and not earring_scale_slider.value_changed.is_connected(_on_earring_scale_changed):
		earring_scale_slider.value_changed.connect(_on_earring_scale_changed)
	if earring_y_offset_slider and not earring_y_offset_slider.value_changed.is_connected(_on_earring_y_offset_changed):
		earring_y_offset_slider.value_changed.connect(_on_earring_y_offset_changed)
	
	# Connect sliders - PIERCING (check if not already connected)
	if piercing_scale_slider and not piercing_scale_slider.value_changed.is_connected(_on_piercing_scale_changed):
		piercing_scale_slider.value_changed.connect(_on_piercing_scale_changed)
	if piercing_y_offset_slider and not piercing_y_offset_slider.value_changed.is_connected(_on_piercing_y_offset_changed):
		piercing_y_offset_slider.value_changed.connect(_on_piercing_y_offset_changed)
	
	# Connect debug options - BOUNDING BOX (check if not already connected)
	if bounding_box_checkbox and not bounding_box_checkbox.toggled.is_connected(_on_bounding_box_toggled):
		bounding_box_checkbox.toggled.connect(_on_bounding_box_toggled)
	
	print("✅ Settings controls connected")

func setup_cascade_options():
	"""Setup cascade selection dropdown"""
	if not cascade_option_button:
		print("⚠️ Cascade option button not found")
		return
	
	# Clear existing items
	cascade_option_button.clear()
	
	# Add cascade options
	cascade_option_button.add_item("Custom Trained Model (my_custom)", 0)
	cascade_option_button.add_item("Bad Face Cascade (Testing)", 1)
	cascade_option_button.add_item("Default Haar Cascade", 2)
	
	# Set default selection (Custom Trained - index 0)
	cascade_option_button.selected = 0
	
	# Update description
	if cascade_desc_label:
		cascade_desc_label.text = "Current: my_custom_face_cascade.xml"
	
	print("✅ Cascade options setup complete")

func _on_settings_pressed():
	"""Show/hide settings panel"""
	if settings_panel:
		settings_panel.visible = not settings_panel.visible
		print("Settings panel visibility:", settings_panel.visible)

func _on_settings_close():
	"""Close settings panel"""
	if settings_panel:
		settings_panel.visible = false
		print("Settings panel closed")

func _on_cascade_selected(index: int):
	"""Handle cascade selection change"""
	var cascade_name = ""
	var cascade_file = ""
	
	match index:
		0:  # Custom Trained
			cascade_name = "my_custom_face_cascade.xml"
			cascade_file = "my_custom_face_cascade.xml"
		1:  # Bad Face Cascade (for testing)
			cascade_name = "bad_face_cascade.xml"
			cascade_file = "bad_face_cascade.xml"
		2:  # Default Haar
			cascade_name = "haarcascade_frontalface_default.xml"
			cascade_file = "haarcascade_frontalface_default.xml"
	
	# Update description label
	if cascade_desc_label:
		cascade_desc_label.text = "Current: %s" % cascade_file
	
	# Send cascade change command to server
	if webcam_manager:
		webcam_manager.send_cascade_change(cascade_file)
		print("Cascade changed to: %s" % cascade_file)
	else:
		print("⚠️ Cannot change cascade - webcam manager not ready")

func _on_settings_apply():
	"""Apply current settings to server"""
	print("=== Applying settings ===")
	
	if not webcam_manager or not webcam_manager.get_connection_status():
		print("Cannot apply settings: Not connected to server")
		if status_label:
			status_label.text = "Connect first before applying settings"
			status_label.modulate = Color(1, 0.5, 0, 0.9)
		return
	
	# Collect current settings
	var settings_data = {
		"hat": {
			"scale_factor": hat_scale_slider.value if hat_scale_slider else 1.2,
			"y_offset_factor": hat_y_offset_slider.value if hat_y_offset_slider else -0.25
		},
		"earring": {
			"scale_factor": earring_scale_slider.value if earring_scale_slider else 0.15,
			"y_offset_factor": earring_y_offset_slider.value if earring_y_offset_slider else 0.65
		},
		"piercing": {
			"scale_factor": piercing_scale_slider.value if piercing_scale_slider else 0.08,
			"y_offset_factor": piercing_y_offset_slider.value if piercing_y_offset_slider else 0.58
		}
	}
	
	print("Settings to apply:", settings_data)
	
	# Send settings to server
	if webcam_manager.has_method("send_settings_update"):
		webcam_manager.send_settings_update(settings_data)
		if status_label:
			status_label.text = "Settings applied successfully!"
			status_label.modulate = Color(0.5, 1, 0.5, 0.9)
		print("✅ Settings sent to server")
	else:
		print("⚠️ Warning: send_settings_update method not available")

func _on_settings_reset():
	"""Reset settings to default values"""
	print("=== Resetting settings to default ===")
	
	# Reset HAT
	if hat_scale_slider:
		hat_scale_slider.value = 1.2
	if hat_scale_value:
		hat_scale_value.text = "1.20"
	if hat_y_offset_slider:
		hat_y_offset_slider.value = -0.25
	if hat_y_offset_value:
		hat_y_offset_value.text = "-0.25"
	
	# Reset EARRING
	if earring_scale_slider:
		earring_scale_slider.value = 0.9
	if earring_scale_value:
		earring_scale_value.text = "0.90"
	if earring_y_offset_slider:
		earring_y_offset_slider.value = 0.65
	if earring_y_offset_value:
		earring_y_offset_value.text = "0.65"
	
	# Reset PIERCING
	if piercing_scale_slider:
		piercing_scale_slider.value = 1.0
	if piercing_scale_value:
		piercing_scale_value.text = "1.00"
	if piercing_y_offset_slider:
		piercing_y_offset_slider.value = 0.58
	if piercing_y_offset_value:
		piercing_y_offset_value.text = "0.58"
	
	# Reset bounding box
	if bounding_box_checkbox:
		bounding_box_checkbox.button_pressed = false
	
	print("✅ Settings reset to default")

# Slider change handlers
func _on_hat_scale_changed(value: float):
	if hat_scale_value:
		hat_scale_value.text = "%.2f" % value

func _on_hat_y_offset_changed(value: float):
	if hat_y_offset_value:
		hat_y_offset_value.text = "%.2f" % value

func _on_earring_scale_changed(value: float):
	if earring_scale_value:
		earring_scale_value.text = "%.2f" % value

func _on_earring_y_offset_changed(value: float):
	if earring_y_offset_value:
		earring_y_offset_value.text = "%.2f" % value

func _on_piercing_scale_changed(value: float):
	if piercing_scale_value:
		piercing_scale_value.text = "%.2f" % value

func _on_piercing_y_offset_changed(value: float):
	if piercing_y_offset_value:
		piercing_y_offset_value.text = "%.2f" % value

func _on_bounding_box_toggled(button_pressed: bool):
	"""Handle bounding box checkbox toggle"""
	if not webcam_manager:
		print("⚠️ Cannot toggle boxes - webcam manager not ready")
		return
	
	if button_pressed:
		# Enable bounding boxes
		webcam_manager.send_command("BOXES:ON")
		print("📦 Bounding boxes enabled")
	else:
		# Disable bounding boxes
		webcam_manager.send_command("BOXES:OFF")
		print("📦 Bounding boxes disabled")

func _on_back_pressed():
	"""Handle back to menu button press"""
	print("=== Back to Menu pressed ===")
	
	# Disconnect from server first
	if webcam_manager:
		webcam_manager.disconnect_from_server()
		print("Disconnected from UDP server")
	
	# Navigate back to main menu
	get_tree().change_scene_to_file("res://MainMenuScene.tscn")
	print("Navigating to Main Menu...")
