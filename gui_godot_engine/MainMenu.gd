extends Control

# UI References (FREE POSITIONING - No Containers)
@onready var start_button = $StartButton
@onready var guide_button = $GuideButton
@onready var credit_button = $CreditButton
@onready var exit_button = $ExitButton

func _ready():
	"""Initialize main menu"""
	print("=== Main Menu Ready ===")
	
	# Connect button signals
	start_button.pressed.connect(_on_start_pressed)
	guide_button.pressed.connect(_on_guide_pressed)
	credit_button.pressed.connect(_on_credit_pressed)
	exit_button.pressed.connect(_on_exit_pressed)
	
	print("Main menu initialized successfully")

func _on_start_pressed():
	"""Navigate to accessory overlay detection"""
	print("Starting Accessory Detection...")
	get_tree().change_scene_to_file("res://UDPAccessoryOverlayScene.tscn")

func _on_guide_pressed():
	"""Navigate to guide page"""
	print("Opening Guide...")
	get_tree().change_scene_to_file("res://GuideScene.tscn")

func _on_credit_pressed():
	"""Navigate to credit page"""
	print("Opening Credits...")
	get_tree().change_scene_to_file("res://CreditScene.tscn")

func _on_exit_pressed():
	"""Exit application"""
	print("Exiting application...")
	get_tree().quit()
