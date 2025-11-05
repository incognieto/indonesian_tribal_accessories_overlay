extends Control

@onready var back_button = $BackButton

func _ready():
	"""Initialize guide scene"""
	print("=== Guide Scene Ready ===")
	
	# Connect back button
	back_button.pressed.connect(_on_back_pressed)

func _on_back_pressed():
	"""Return to main menu"""
	print("Returning to main menu...")
	get_tree().change_scene_to_file("res://MainMenuScene.tscn")
