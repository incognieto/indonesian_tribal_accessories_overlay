#!/usr/bin/env python3
"""
UDP Webcam Server with Face Detection & Accessory Overlay
Integrated with CV Accessory Overlay System
"""

import cv2
import socket
import struct
import threading
import time
import math
import sys
import argparse
from pathlib import Path

# Add parent directory to path to import pipelines
sys.path.insert(0, str(Path(__file__).parent.parent))

from pipelines.infer import FaceDetector, InferencePipeline
from pipelines.overlay import AccessoryOverlay
from pipelines.features import FeaturePipeline
from pipelines.train import SVMTrainer
from pipelines.utils import load_json


class UDPWebcamOverlayServer:
    def __init__(self, host='127.0.0.1', port=8888, use_overlay=True, use_svm=False, mirror=True, show_boxes=True):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = set()
        self.camera = None
        self.running = False
        self.sequence_number = 0
        
        # Optimized settings
        self.max_packet_size = 32768  # 32KB packets
        self.target_fps = 15
        self.jpeg_quality = 40
        self.frame_width = 480
        self.frame_height = 360
        
        # Performance monitoring
        self.frame_send_time = 1.0 / self.target_fps
        
        # Camera settings
        self.mirror = mirror
        
        # Face detection & overlay
        self.use_overlay = use_overlay
        self.use_svm = use_svm
        self.show_boxes = show_boxes  # Show bounding boxes
        self.detector = None
        self.overlay_system = None
        self.accessories = {}
        self.all_accessory_variants = {}  # Store all loaded variants
        self.accessory_packages = {}  # Predefined packages
        self.current_package = 1  # Current active package
        self.inference_pipeline = None
        
    def initialize_face_detection(self, cascade_dir='../assets/cascades', 
                                   models_dir='../models',
                                   config_path='../assets/overlay_config.json',
                                   accessories_config=None):
        """Initialize face detection and overlay system."""
        print("\n🎭 Initializing Face Detection & Overlay System...")
        
        try:
            # Load config
            config = None
            config_file = Path(config_path)
            if config_file.exists():
                config = load_json(config_file)
                print(f"✅ Loaded overlay config from {config_path}")
            
            # Load feature pipeline and SVM if needed
            feature_pipeline = None
            trainer = None
            
            if self.use_svm:
                print("📊 Loading SVM classifier...")
                models_path = Path(models_dir)
                
                feature_pipeline = FeaturePipeline()
                feature_pipeline.load(models_path)
                
                trainer = SVMTrainer()
                model_file = models_path / 'svm_face_linear.pkl'
                if not model_file.exists():
                    print(f"⚠️ SVM model not found at {model_file}, using Haar only")
                    self.use_svm = False
                else:
                    trainer.load(model_file)
                    print("✅ SVM classifier loaded")
            
            # Create detector
            self.detector = FaceDetector(
                cascade_dir=Path(cascade_dir),
                feature_pipeline=feature_pipeline,
                svm_trainer=trainer,
                config=config
            )
            print("✅ Face detector initialized")
            
            # Load ALL accessory variants if overlay enabled
            if self.use_overlay:
                print("🎨 Loading all accessory variants...")
                variants_dir = Path('../assets/variants')
                
                if not variants_dir.exists():
                    print(f"⚠️ Variants directory not found: {variants_dir}")
                else:
                    import glob
                    overlay = AccessoryOverlay()
                    
                    # Group by type
                    self.all_accessory_variants = {
                        'hat': [],
                        'earring_left': [],
                        'earring_right': [],
                        'piercing_nose': [],
                        'tattoo_face': []
                    }
                    
                    # Load all variants for each type
                    for acc_type in ['hat', 'earring_left', 'earring_right', 'piercing_nose', 'tattoo_face']:
                        pattern = f"{acc_type}_*.png"
                        files = glob.glob(str(variants_dir / pattern))
                        
                        print(f"\n  🔍 Loading {acc_type} variants:")
                        for file_path in files:
                            # CRITICAL: Load image directly without using cache
                            # Cache causes all variants to reference the same image!
                            from pipelines.utils import load_image_rgba
                            variant_img = load_image_rgba(Path(file_path))
                            
                            variant_name = Path(file_path).stem
                            
                            # Extract color from filename (e.g., "hat_red" -> "red")
                            variant_color = variant_name.split('_')[-1] if '_' in variant_name else 'default'
                            
                            print(f"     - {variant_name} → color='{variant_color}' (shape={variant_img.shape if variant_img is not None else 'None'})")
                            
                            self.all_accessory_variants[acc_type].append({
                                'name': variant_name,
                                'color': variant_color,
                                'path': str(file_path),
                                'image': variant_img
                            })
                        
                        if self.all_accessory_variants[acc_type]:
                            print(f"  ✅ Loaded {len(self.all_accessory_variants[acc_type])} variants for {acc_type}")
                        else:
                            print(f"  ⚠️ No variants found for {acc_type}")
                    
                    # Create predefined packages
                    self._create_accessory_packages()
                    
                    # Set initial package
                    self._set_package(1)
            
            # Create overlay system
            self.overlay_system = AccessoryOverlay(
                config_path=config_file if config_file.exists() else None
            )
            print("✅ Overlay system initialized")
            
            # Create inference pipeline
            self.inference_pipeline = InferencePipeline(
                self.detector,
                self.overlay_system,
                self.accessories
            )
            print("✅ Inference pipeline ready")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize face detection: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _create_accessory_packages(self):
        """Create predefined accessory packages with different color combinations."""
        print("\n📦 Creating accessory packages...")
        print(f"📊 Available variants per type:")
        for acc_type, variants in self.all_accessory_variants.items():
            if variants:
                colors = [v['color'] for v in variants]
                print(f"   {acc_type}: {colors}")
        
        # Helper to find variant by color
        def find_variant(acc_type, color):
            print(f"   🔍 Looking for {acc_type} with color '{color}'...")
            for variant in self.all_accessory_variants.get(acc_type, []):
                if variant['color'] == color:
                    print(f"      ✅ Found: {variant['name']}")
                    return variant['image']
            # Fallback to first available
            variants = self.all_accessory_variants.get(acc_type, [])
            if variants:
                print(f"      ⚠️ NOT FOUND! Using fallback: {variants[0]['color']} ({variants[0]['name']})")
                return variants[0]['image']
            else:
                print(f"      ❌ No variants available!")
                return None
        
        print("\n🎨 Package 1: Red & Gold")
        
        # Package 1: Red/Gold theme (Asmat)
        self.accessory_packages[1] = {
            'name': 'Suku Asmat',
            'description': 'Classic elegant look',
            'accessories': {
                'hat': find_variant('hat', 'red'),
                'earring_left': find_variant('earring_left', 'gold'),
                'earring_right': find_variant('earring_right', 'gold'),
                'piercing_nose': find_variant('piercing_nose', 'silver'),
            }
        }
        
        # Package 2: Blue/Silver theme (Gayo)
        self.accessory_packages[2] = {
            'name': 'Suku Gayo',
            'description': 'Cool modern style',
            'accessories': {
                'hat': find_variant('hat', 'blue'),
                #'earring_left': find_variant('earring_left', 'silver'),
                #'earring_right': find_variant('earring_right', 'silver'),
                #'piercing_nose': find_variant('piercing_nose', 'blue'),
            }
        }
        
        # Package 3: Green/Diamond theme (Jawa)
        self.accessory_packages[3] = {
            'name': 'Suku Jawa',
            'description': 'Fresh natural vibe',
            'accessories': {
                'hat': find_variant('hat', 'green'),
                'earring_left': find_variant('earring_left', 'diamond'),
                'earring_right': find_variant('earring_right', 'diamond'),
                #'piercing_nose': find_variant('piercing_nose', 'green'),
            }
        }
        
        # Package 4: Pink/Purple theme (Minang)
        self.accessory_packages[4] = {
            'name': 'Suku Minang',
            'description': 'Cute playful look',
            'accessories': {
                'hat': find_variant('hat', 'pink'),
                'earring_left': find_variant('earring_left', 'pink'),
                'earring_right': find_variant('earring_right', 'pink'),
                #'piercing_nose': find_variant('piercing_nose', 'pink'),
            }
        }
        
        # Package 5: Rainbow/Mixed theme (Bugis)
        self.accessory_packages[5] = {
            'name': 'Suku Bugis',
            'description': 'Bold colorful style',
            'accessories': {
                'hat': find_variant('hat', 'yellow'),
                'earring_left': find_variant('earring_left', 'red'),
                'earring_right': find_variant('earring_right', 'blue'),
                #'piercing_nose': find_variant('piercing_nose', 'black'),
            }
        }
        
        for pkg_id, pkg_data in self.accessory_packages.items():
            print(f"  📦 Package {pkg_id}: {pkg_data['name']} - {pkg_data['description']}")
    
    def _set_package(self, package_id: int):
        """Set active accessory package."""
        if package_id not in self.accessory_packages:
            print(f"⚠️ Package {package_id} not found, using package 1")
            package_id = 1
        
        package = self.accessory_packages[package_id]
        
        # CRITICAL: Must create new dict to avoid reference issues
        new_accessories = {}
        for acc_type, acc_img in package['accessories'].items():
            new_accessories[acc_type] = acc_img
        
        print(f"\n{'='*60}")
        print(f"🔄 SWITCHING PACKAGE FROM {self.current_package} TO {package_id}")
        print(f"{'='*60}")
        
        # Debug: Show what's changing
        print(f"📋 OLD accessories: {list(self.accessories.keys()) if hasattr(self, 'accessories') else 'None'}")
        print(f"📋 NEW accessories: {list(new_accessories.keys())}")
        
        self.accessories = new_accessories
        self.current_package = package_id
        
        # Update inference pipeline - THIS IS KEY!
        if self.inference_pipeline:
            # FORCE update the reference
            self.inference_pipeline.accessories = self.accessories
            print(f"🔧 Pipeline updated with {len(self.inference_pipeline.accessories)} accessories")
            
            # Debug: Verify the images are different
            for key in ['hat', 'earring_left', 'piercing_nose']:
                if key in self.accessories:
                    img = self.accessories[key]
                    print(f"   ✓ {key}: shape={img.shape if img is not None else 'None'}")
        
        print(f"✨ SWITCHED TO: Package {package_id} - {package['name']}")
        print(f"� Description: {package['description']}")
        print(f"{'='*60}\n")
        
        return package
    
    def change_package(self, package_id: int):
        """Change accessory package (can be called from UDP command)."""
        return self._set_package(package_id)
    
    def _apply_settings_update(self, settings_data: dict):
        """
        Apply manual settings update to overlay system.
        
        Args:
            settings_data: Dictionary containing settings for each accessory type
                Example: {
                    "hat": {"scale_factor": 1.5, "y_offset_factor": -0.3},
                    "earring": {"scale_factor": 0.2, "y_offset_factor": 0.7},
                    "piercing": {"scale_factor": 0.1, "y_offset_factor": 0.6}
                }
        """
        print("\n" + "="*60)
        print("⚙️ APPLYING MANUAL SETTINGS UPDATE")
        print("="*60)
        
        if not self.overlay_system:
            print("❌ Overlay system not initialized")
            return
        
        # Update overlay system config
        for acc_type, settings in settings_data.items():
            if acc_type == "hat":
                config_key = "hat"
            elif acc_type == "earring":
                # Apply to both left and right earrings
                for key in ["earring_left", "earring_right"]:
                    if key not in self.overlay_system.config:
                        self.overlay_system.config[key] = {}
                    self.overlay_system.config[key].update(settings)
                    print(f"  ✓ Updated {key}: {settings}")
                continue
            elif acc_type == "piercing":
                config_key = "piercing_nose"
            else:
                config_key = acc_type
            
            if config_key not in self.overlay_system.config:
                self.overlay_system.config[config_key] = {}
            
            self.overlay_system.config[config_key].update(settings)
            print(f"  ✓ Updated {config_key}: {settings}")
        
        print("✅ Settings applied to overlay system")
        print("="*60 + "\n")
    
    def _change_cascade(self, cascade_file: str):
        """
        Change the active face detection cascade.
        
        Args:
            cascade_file: Name of cascade XML file (e.g., "my_custom_face_cascade.xml")
        """
        print("\n" + "="*60)
        print(f"🔄 CHANGING FACE DETECTION CASCADE")
        print("="*60)
        
        if not self.detector:
            print("❌ Face detector not initialized")
            return
        
        # Build full path
        cascade_path = Path(self.detector.cascade_dir) / cascade_file
        
        if not cascade_path.exists():
            print(f"❌ Cascade file not found: {cascade_path}")
            raise FileNotFoundError(f"Cascade not found: {cascade_file}")
        
        # Load new cascade
        new_cascade = cv2.CascadeClassifier(str(cascade_path))
        
        if new_cascade.empty():
            print(f"❌ Failed to load cascade: {cascade_path}")
            raise ValueError(f"Invalid cascade file: {cascade_file}")
        
        # Replace the cascade in detector
        self.detector.cascades['face_default'] = new_cascade
        
        print(f"  ✓ Loaded: {cascade_path}")
        print(f"  ✓ File size: {cascade_path.stat().st_size} bytes")
        print(f"✅ Cascade changed successfully to {cascade_file}")
        print("="*60 + "\n")
    
    def initialize_camera(self):
        print("🎥 Initializing optimized camera...")
        
        import platform
        
        backends_to_try = []
        
        # Detect platform
        system = platform.system()
        if system == "Windows":
            backends_to_try = [cv2.CAP_DSHOW, cv2.CAP_ANY]
        elif system == "Linux":
            backends_to_try = [cv2.CAP_V4L2, cv2.CAP_ANY]
        else:  # macOS or other
            backends_to_try = [cv2.CAP_ANY]
        
        print(f"📌 Platform: {system}")
        
        # Try each backend
        for backend in backends_to_try:
            backend_name = {
                cv2.CAP_DSHOW: "DirectShow",
                cv2.CAP_V4L2: "V4L2",
                cv2.CAP_ANY: "Auto"
            }.get(backend, "Unknown")
            
            print(f"🔍 Trying backend: {backend_name}...")
            
            self.camera = cv2.VideoCapture(0, backend)
            
            if self.camera.isOpened():
                # Set optimized resolution
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
                self.camera.set(cv2.CAP_PROP_FPS, self.target_fps)
                self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimal buffer
                
                ret, frame = self.camera.read()
                if ret and frame is not None:
                    actual_width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
                    actual_height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    print(f"✅ Camera ready with {backend_name}")
                    print(f"📐 Resolution: {actual_width}x{actual_height} @ {self.target_fps}FPS")
                    return True
                else:
                    print(f"⚠️ {backend_name} opened but can't read frame")
                    self.camera.release()
            else:
                print(f"❌ {backend_name} failed to open")
        
        print("❌ Camera initialization failed - No working backend found")
        print("💡 Troubleshooting tips:")
        print("   1. Check if webcam is connected: ls /dev/video*")
        print("   2. Check permissions: sudo usermod -a -G video $USER")
        print("   3. Test with: ffplay /dev/video0")
        return False
    
    def start_server(self):
        if not self.initialize_camera():
            return
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 655360)  # 640KB send buffer
        self.server_socket.bind((self.host, self.port))
        
        print(f"\n🚀 UDP Server: {self.host}:{self.port}")
        print(f"📊 Settings: {self.frame_width}x{self.frame_height}, {self.target_fps}FPS, Q{self.jpeg_quality}")
        print(f"🎭 Overlay: {'Enabled' if self.use_overlay else 'Disabled'}")
        print(f"🤖 SVM: {'Enabled' if self.use_svm else 'Disabled'}")
        
        if self.use_overlay and len(self.accessories) > 0:
            print(f"🎨 Loaded accessories: {', '.join(self.accessories.keys())}")
            
            # Show which overlay types will be enabled
            enabled_types = []
            if 'hat' in self.accessories:
                enabled_types.append('hat')
            if 'earring_left' in self.accessories or 'earring_right' in self.accessories:
                enabled_types.append('earrings')
            if 'piercing_nose' in self.accessories:
                enabled_types.append('piercing')
            if 'tattoo_face' in self.accessories:
                enabled_types.append('tattoo')
            print(f"✨ Active overlays: {', '.join(enabled_types)}")
        
        print("\n⏳ Waiting for clients...")
        
        self.running = True
        
        # Start threads
        threading.Thread(target=self.listen_for_clients, daemon=True).start()
        threading.Thread(target=self._broadcast_frames, daemon=True).start()
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
        finally:
            self.stop_server()
    
    def listen_for_clients(self):
        self.server_socket.settimeout(1.0)
        
        while self.running:
            try:
                data, addr = self.server_socket.recvfrom(1024)
                message = data.decode('utf-8')
                
                if message == "REGISTER":
                    if addr not in self.clients:
                        self.clients.add(addr)
                        print(f"✅ Client connected: {addr} (Total: {len(self.clients)})")
                    
                    self.server_socket.sendto("REGISTERED".encode('utf-8'), addr)
                
                elif message == "UNREGISTER":
                    self.clients.discard(addr)
                    print(f"❌ Client disconnected: {addr}")
                
                elif message.startswith("PACKAGE:"):
                    # Handle package switch command
                    print(f"📨 Received package command: {message} from {addr}")
                    try:
                        package_id = int(message.split(":")[1])
                        print(f"🔄 Switching to package {package_id}...")
                        package = self.change_package(package_id)
                        response = f"PACKAGE_SET:{package_id}:{package['name']}"
                        self.server_socket.sendto(response.encode('utf-8'), addr)
                        print(f"✅ Package switched successfully: {package['name']}")
                    except (ValueError, IndexError, KeyError) as e:
                        print(f"❌ Package switch error: {e}")
                        error_msg = f"PACKAGE_ERROR:Invalid package ID"
                        self.server_socket.sendto(error_msg.encode('utf-8'), addr)
                
                elif message.startswith("SETTINGS:"):
                    # Handle settings update command
                    print(f"⚙️ Received settings update from {addr}")
                    try:
                        import json
                        settings_json = message[9:]  # Remove "SETTINGS:" prefix
                        settings_data = json.loads(settings_json)
                        print(f"📝 Settings data: {settings_data}")
                        
                        # Apply settings to overlay system
                        if self.overlay_system:
                            self._apply_settings_update(settings_data)
                            response = "SETTINGS_APPLIED"
                            print(f"✅ Settings applied successfully")
                        else:
                            response = "SETTINGS_ERROR:Overlay system not initialized"
                            print(f"❌ Overlay system not initialized")
                        
                        self.server_socket.sendto(response.encode('utf-8'), addr)
                    except (json.JSONDecodeError, Exception) as e:
                        print(f"❌ Settings update error: {e}")
                        error_msg = f"SETTINGS_ERROR:{str(e)}"
                        self.server_socket.sendto(error_msg.encode('utf-8'), addr)
                
                elif message.startswith("CASCADE:"):
                    # Handle cascade change command
                    print(f"🔄 Received cascade change command from {addr}")
                    try:
                        cascade_file = message[8:]  # Remove "CASCADE:" prefix
                        print(f"📝 Switching to cascade: {cascade_file}")
                        
                        # Change the cascade in face detector
                        if self.detector:
                            self._change_cascade(cascade_file)
                            response = f"CASCADE_CHANGED:{cascade_file}"
                            print(f"✅ Cascade changed successfully to {cascade_file}")
                        else:
                            response = "CASCADE_ERROR:Detector not initialized"
                            print(f"❌ Detector not initialized")
                        
                        self.server_socket.sendto(response.encode('utf-8'), addr)
                    except Exception as e:
                        print(f"❌ Cascade change error: {e}")
                        error_msg = f"CASCADE_ERROR:{str(e)}"
                        self.server_socket.sendto(error_msg.encode('utf-8'), addr)
                
                elif message == "BOXES:ON":
                    # Enable bounding boxes
                    self.show_boxes = True
                    print(f"📦 Bounding boxes enabled")
                    self.server_socket.sendto("BOXES_ENABLED".encode('utf-8'), addr)
                
                elif message == "BOXES:OFF":
                    # Disable bounding boxes
                    self.show_boxes = False
                    print(f"📦 Bounding boxes disabled")
                    self.server_socket.sendto("BOXES_DISABLED".encode('utf-8'), addr)
                    
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"⚠️ Client error: {e}")
    
    def _broadcast_frames(self):
        last_frame_time = 0
        frame_count = 0
        
        while self.running:
            current_time = time.time()
            
            # Skip if no clients
            if len(self.clients) == 0:
                time.sleep(0.1)
                continue
            
            # Frame rate control
            if current_time - last_frame_time < self.frame_send_time:
                time.sleep(0.01)
                continue
            
            ret, frame = self.camera.read()
            if not ret:
                break
            
            # Apply mirror mode (flip horizontally for natural selfie view)
            if self.mirror:
                frame = cv2.flip(frame, 1)
            
            # Apply face detection and overlay if enabled
            if self.use_overlay and self.inference_pipeline:
                try:
                    # CRITICAL: Force update pipeline accessories from current package
                    # This ensures threading doesn't cause stale reference
                    self.inference_pipeline.accessories = self.accessories
                    
                    # Map loaded accessories to enabled types
                    # Overlay system uses shorthand: 'hat', 'ear', 'piercing', 'tattoo'
                    enabled_accessories = []
                    if 'hat' in self.accessories:
                        enabled_accessories.append('hat')
                    if 'earring_left' in self.accessories or 'earring_right' in self.accessories:
                        enabled_accessories.append('ear')
                    if 'piercing_nose' in self.accessories:
                        enabled_accessories.append('piercing')
                    if 'tattoo_face' in self.accessories:
                        enabled_accessories.append('tattoo')
                    
                    frame = self.inference_pipeline.process_image(
                        frame,
                        enabled_accessories=enabled_accessories,
                        use_svm=self.use_svm,
                        visualize_boxes=self.show_boxes  # Show bounding boxes if enabled
                    )
                    
                    # Add visual indicator showing current package
                    pkg_name = self.accessory_packages.get(self.current_package, {}).get('name', 'Unknown')
                    cv2.putText(
                        frame,
                        f"Package {self.current_package}: {pkg_name}",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 0),
                        2
                    )
                    
                except Exception as e:
                    # If overlay fails, just send original frame
                    if frame_count % 100 == 0:  # Log occasionally
                        print(f"⚠️ Overlay error: {e}")
            
            # Encode with optimized settings
            encode_param = [cv2.IMWRITE_JPEG_QUALITY, self.jpeg_quality]
            result, encoded_img = cv2.imencode('.jpg', frame, encode_param)
            
            if result:
                frame_data = encoded_img.tobytes()
                self.send_frame_to_clients(frame_data)
                last_frame_time = current_time
                frame_count += 1
    
    def send_frame_to_clients(self, frame_data):
        if not frame_data or len(self.clients) == 0:
            return
        
        self.sequence_number = (self.sequence_number + 1) % 65536
        frame_size = len(frame_data)
        
        header_size = 12
        payload_size = self.max_packet_size - header_size
        total_packets = math.ceil(frame_size / payload_size)
        
        # Send to all clients efficiently
        for client_addr in self.clients.copy():
            try:
                for packet_index in range(total_packets):
                    start_pos = packet_index * payload_size
                    end_pos = min(start_pos + payload_size, frame_size)
                    
                    header = struct.pack("!III", self.sequence_number, total_packets, packet_index)
                    udp_packet = header + frame_data[start_pos:end_pos]
                    
                    self.server_socket.sendto(udp_packet, client_addr)
                
                # Less frequent logging
                if self.sequence_number % 60 == 1:  # Every 4 seconds at 15FPS
                    print(f"📤 Frame {self.sequence_number}: {frame_size//1024}KB → {len(self.clients)} clients")
                    
            except Exception as e:
                print(f"❌ Send error to {client_addr}: {e}")
                self.clients.discard(client_addr)
    
    def stop_server(self):
        print("⏹️ Stopping server...")
        self.running = False
        
        if self.server_socket:
            self.server_socket.close()
        if self.camera:
            self.camera.release()
        
        print("✅ Server stopped")


def main():
    parser = argparse.ArgumentParser(description='UDP Webcam Server with Face Detection & Overlay')
    
    # Server settings
    parser.add_argument('--host', default='127.0.0.1', help='Server host (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8888, help='Server port (default: 8888)')
    
    # Overlay settings
    parser.add_argument('--no-overlay', action='store_true', help='Disable overlay system')
    parser.add_argument('--use-svm', action='store_true', help='Enable SVM face validation')
    parser.add_argument('--no-boxes', action='store_true', help='Disable bounding boxes')
    
    # Paths
    parser.add_argument('--cascade-dir', default='../assets/cascades', help='Haar cascades directory')
    parser.add_argument('--models-dir', default='../models', help='Models directory (for SVM)')
    parser.add_argument('--config', default='../assets/overlay_config.json', help='Overlay config file')
    
    # Accessories
    parser.add_argument('--hat', help='Hat accessory image path')
    parser.add_argument('--ear-left', help='Left earring image path')
    parser.add_argument('--ear-right', help='Right earring image path')
    parser.add_argument('--piercing', help='Nose piercing image path')
    parser.add_argument('--tattoo-face', help='Face tattoo image path')
    
    # Quick presets
    parser.add_argument('--load-samples', action='store_true', help='Load sample accessories from assets/variants')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("  UDP WEBCAM SERVER - FACE DETECTION & ACCESSORY OVERLAY")
    print("=" * 70)
    
    # Create server
    server = UDPWebcamOverlayServer(
        host=args.host,
        port=args.port,
        use_overlay=not args.no_overlay,
        use_svm=args.use_svm,
        show_boxes=not args.no_boxes
    )
    
    # Initialize face detection if overlay enabled
    if not args.no_overlay:
        accessories_config = {}
        
        # Load from arguments
        if args.hat:
            accessories_config['hat'] = args.hat
        if args.ear_left:
            accessories_config['earring_left'] = args.ear_left
        if args.ear_right:
            accessories_config['earring_right'] = args.ear_right
        if args.piercing:
            accessories_config['piercing_nose'] = args.piercing
        if args.tattoo_face:
            accessories_config['tattoo_face'] = args.tattoo_face
        
        # Or load samples
        if args.load_samples:
            variants_dir = Path('../assets/variants')
            if variants_dir.exists():
                # Use first available variant for each accessory type
                import glob
                
                def find_first_variant(pattern):
                    """Find first matching file for a pattern."""
                    files = glob.glob(str(variants_dir / pattern))
                    return files[0] if files else None
                
                hat_file = find_first_variant('hat_*.png')
                ear_l_file = find_first_variant('earring_left_*.png')
                ear_r_file = find_first_variant('earring_right_*.png')
                piercing_file = find_first_variant('piercing_nose_*.png')
                
                if hat_file:
                    accessories_config['hat'] = hat_file
                if ear_l_file:
                    accessories_config['earring_left'] = ear_l_file
                if ear_r_file:
                    accessories_config['earring_right'] = ear_r_file
                if piercing_file:
                    accessories_config['piercing_nose'] = piercing_file
                
                print(f"📂 Loading from: {variants_dir}")
            else:
                print(f"⚠️ Variants directory not found: {variants_dir}")
        
        if not server.initialize_face_detection(
            cascade_dir=args.cascade_dir,
            models_dir=args.models_dir,
            config_path=args.config,
            accessories_config=accessories_config if accessories_config else None
        ):
            print("\n⚠️ Face detection initialization failed!")
            print("Server will run without overlay.")
            server.use_overlay = False
    
    # Start server
    print("\n" + "=" * 70)
    server.start_server()


if __name__ == "__main__":
    main()
