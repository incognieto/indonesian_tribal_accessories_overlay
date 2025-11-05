extends Panel

"""
Accessory Settings Panel
Allows manual adjustment of accessory parameters (scale, position, etc.)
"""

# Signals
signal settings_changed(settings_data: Dictionary)
signal settings_applied(settings_data: Dictionary)

# Node references - HAT
@onready var hat_scale_slider = $VBoxContainer/ScrollContainer/SettingsContent/HatSection/HatScaleSlider
@onready var hat_scale_value = $VBoxContainer/ScrollContainer/SettingsContent/HatSection/HatScaleContainer/HatScaleValue
@onready var hat_y_offset_slider = $VBoxContainer/ScrollContainer/SettingsContent/HatSection/HatYOffsetSlider
@onready var hat_y_offset_value = $VBoxContainer/ScrollContainer/SettingsContent/HatSection/HatYOffsetContainer/HatYOffsetValue
@onready var hat_rotation_toggle = $VBoxContainer/ScrollContainer/SettingsContent/HatSection/HatRotationToggle

# Node references - EARRING
@onready var earring_scale_slider = $VBoxContainer/ScrollContainer/SettingsContent/EarringSection/EarringScaleSlider
@onready var earring_scale_value = $VBoxContainer/ScrollContainer/SettingsContent/EarringSection/EarringScaleContainer/EarringScaleValue
@onready var earring_x_offset_slider = $VBoxContainer/ScrollContainer/SettingsContent/EarringSection/EarringXOffsetSlider
@onready var earring_x_offset_value = $VBoxContainer/ScrollContainer/SettingsContent/EarringSection/EarringXOffsetContainer/EarringXOffsetValue
@onready var earring_y_offset_slider = $VBoxContainer/ScrollContainer/SettingsContent/EarringSection/EarringYOffsetSlider
@onready var earring_y_offset_value = $VBoxContainer/ScrollContainer/SettingsContent/EarringSection/EarringYOffsetContainer/EarringYOffsetValue

# Node references - PIERCING
@onready var piercing_scale_slider = $VBoxContainer/ScrollContainer/SettingsContent/PiercingSection/PiercingScaleSlider
@onready var piercing_scale_value = $VBoxContainer/ScrollContainer/SettingsContent/PiercingSection/PiercingScaleContainer/PiercingScaleValue
@onready var piercing_x_offset_slider = $VBoxContainer/ScrollContainer/SettingsContent/PiercingSection/PiercingXOffsetSlider
@onready var piercing_x_offset_value = $VBoxContainer/ScrollContainer/SettingsContent/PiercingSection/PiercingXOffsetContainer/PiercingXOffsetValue
@onready var piercing_y_offset_slider = $VBoxContainer/ScrollContainer/SettingsContent/PiercingSection/PiercingYOffsetSlider
@onready var piercing_y_offset_value = $VBoxContainer/ScrollContainer/SettingsContent/PiercingSection/PiercingYOffsetContainer/PiercingYOffsetValue

# Buttons
@onready var apply_button = $VBoxContainer/ButtonsContainer/ApplyButton
@onready var reset_button = $VBoxContainer/ButtonsContainer/ResetButton
@onready var close_button = $VBoxContainer/CloseButton

# Default values
var default_settings = {
	"hat": {
		"scale_factor": 1.2,
		"y_offset_factor": -0.25,
		"rotation_enabled": true
	},
	"earring": {
		"scale_factor": 0.15,
		"x_offset_factor": 0.45,
		"y_offset_factor": 0.65
	},
	"piercing_nose": {
		"scale_factor": 0.08,
		"x_offset_factor": 0.05,
		"y_offset_factor": 0.58
	}
}

func _ready():
	"""Initialize the settings panel"""
	print("=== AccessorySettingsPanel._ready() ===")
	
	# Connect slider signals
	connect_hat_signals()
	connect_earring_signals()
	connect_piercing_signals()
	
	# Connect button signals
	apply_button.pressed.connect(_on_apply_pressed)
	reset_button.pressed.connect(_on_reset_pressed)
	close_button.pressed.connect(_on_close_pressed)
	
	# Load default values
	load_default_settings()
	
	print("Settings panel initialized")

func connect_hat_signals():
	"""Connect hat control signals"""
	hat_scale_slider.value_changed.connect(_on_hat_scale_changed)
	hat_y_offset_slider.value_changed.connect(_on_hat_y_offset_changed)
	hat_rotation_toggle.toggled.connect(_on_hat_rotation_toggled)

func connect_earring_signals():
	"""Connect earring control signals"""
	earring_scale_slider.value_changed.connect(_on_earring_scale_changed)
	earring_x_offset_slider.value_changed.connect(_on_earring_x_offset_changed)
	earring_y_offset_slider.value_changed.connect(_on_earring_y_offset_changed)

func connect_piercing_signals():
	"""Connect piercing control signals"""
	piercing_scale_slider.value_changed.connect(_on_piercing_scale_changed)
	piercing_x_offset_slider.value_changed.connect(_on_piercing_x_offset_changed)
	piercing_y_offset_slider.value_changed.connect(_on_piercing_y_offset_changed)

# HAT Callbacks
func _on_hat_scale_changed(value: float):
	hat_scale_value.text = "%.2f" % value
	emit_settings_changed()

func _on_hat_y_offset_changed(value: float):
	hat_y_offset_value.text = "%.2f" % value
	emit_settings_changed()

func _on_hat_rotation_toggled(toggled: bool):
	emit_settings_changed()

# EARRING Callbacks
func _on_earring_scale_changed(value: float):
	earring_scale_value.text = "%.2f" % value
	emit_settings_changed()

func _on_earring_x_offset_changed(value: float):
	earring_x_offset_value.text = "%.2f" % value
	emit_settings_changed()

func _on_earring_y_offset_changed(value: float):
	earring_y_offset_value.text = "%.2f" % value
	emit_settings_changed()

# PIERCING Callbacks
func _on_piercing_scale_changed(value: float):
	piercing_scale_value.text = "%.2f" % value
	emit_settings_changed()

func _on_piercing_x_offset_changed(value: float):
	piercing_x_offset_value.text = "%.2f" % value
	emit_settings_changed()

func _on_piercing_y_offset_changed(value: float):
	piercing_y_offset_value.text = "%.2f" % value
	emit_settings_changed()

func emit_settings_changed():
	"""Emit signal when any setting changes"""
	var current_settings = get_current_settings()
	settings_changed.emit(current_settings)

func get_current_settings() -> Dictionary:
	"""Get current settings from all controls"""
	return {
		"hat": {
			"scale_factor": hat_scale_slider.value,
			"y_offset_factor": hat_y_offset_slider.value,
			"rotation_enabled": hat_rotation_toggle.button_pressed
		},
		"earring_left": {
			"scale_factor": earring_scale_slider.value,
			"x_offset_factor": -earring_x_offset_slider.value,  # Negative for left
			"y_offset_factor": earring_y_offset_slider.value
		},
		"earring_right": {
			"scale_factor": earring_scale_slider.value,
			"x_offset_factor": earring_x_offset_slider.value,  # Positive for right
			"y_offset_factor": earring_y_offset_slider.value
		},
		"piercing_nose": {
			"scale_factor": piercing_scale_slider.value,
			"x_offset_factor": piercing_x_offset_slider.value,
			"y_offset_factor": piercing_y_offset_slider.value
		}
	}

func load_default_settings():
	"""Load default settings into controls"""
	print("Loading default settings...")
	
	# HAT
	hat_scale_slider.value = default_settings.hat.scale_factor
	hat_y_offset_slider.value = default_settings.hat.y_offset_factor
	hat_rotation_toggle.button_pressed = default_settings.hat.rotation_enabled
	
	# EARRING
	earring_scale_slider.value = default_settings.earring.scale_factor
	earring_x_offset_slider.value = default_settings.earring.x_offset_factor
	earring_y_offset_slider.value = default_settings.earring.y_offset_factor
	
	# PIERCING
	piercing_scale_slider.value = default_settings.piercing_nose.scale_factor
	piercing_x_offset_slider.value = default_settings.piercing_nose.x_offset_factor
	piercing_y_offset_slider.value = default_settings.piercing_nose.y_offset_factor
	
	# Update value labels
	_update_all_value_labels()

func _update_all_value_labels():
	"""Update all value display labels"""
	hat_scale_value.text = "%.2f" % hat_scale_slider.value
	hat_y_offset_value.text = "%.2f" % hat_y_offset_slider.value
	
	earring_scale_value.text = "%.2f" % earring_scale_slider.value
	earring_x_offset_value.text = "%.2f" % earring_x_offset_slider.value
	earring_y_offset_value.text = "%.2f" % earring_y_offset_slider.value
	
	piercing_scale_value.text = "%.2f" % piercing_scale_slider.value
	piercing_x_offset_value.text = "%.2f" % piercing_x_offset_slider.value
	piercing_y_offset_value.text = "%.2f" % piercing_y_offset_slider.value

func _on_apply_pressed():
	"""Apply current settings"""
	var current_settings = get_current_settings()
	print("Applying settings:", current_settings)
	settings_applied.emit(current_settings)

func _on_reset_pressed():
	"""Reset to default settings"""
	print("Resetting to default settings")
	load_default_settings()
	emit_settings_changed()

func _on_close_pressed():
	"""Close the settings panel"""
	hide()

func show_panel():
	"""Show the settings panel"""
	show()

func hide_panel():
	"""Hide the settings panel"""
	hide()
