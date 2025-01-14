from esphome import pins
import esphome.codegen as cg
from esphome.components import display, spi
import esphome.config_validation as cv
from esphome.const import (
    CONF_CONTRAST,
    CONF_CS_PIN,
    CONF_DC_PIN,
    CONF_ID,
    CONF_LAMBDA,
    CONF_PAGES,
    CONF_RESET_PIN,
)

DEPENDENCIES = ["spi"]

pcd8544_ns = cg.esphome_ns.namespace("pcd8544")
PCD8544 = pcd8544_ns.class_(
    "PCD8544", cg.PollingComponent, display.DisplayBuffer, spi.SPIDevice
)


CONFIG_SCHEMA = cv.All(
    display.FULL_DISPLAY_SCHEMA.extend(
        {
            cv.GenerateID(): cv.declare_id(PCD8544),
            cv.Required(CONF_DC_PIN): pins.gpio_output_pin_schema,
            cv.Required(CONF_RESET_PIN): pins.gpio_output_pin_schema,
            cv.Required(CONF_CS_PIN): pins.gpio_output_pin_schema,  # CE
            cv.Optional(CONF_CONTRAST, default=0x7F): cv.int_,
        }
    )
    .extend(cv.polling_component_schema("1s"))
    .extend(spi.spi_device_schema()),
    cv.has_at_most_one_key(CONF_PAGES, CONF_LAMBDA),
)

FINAL_VALIDATE_SCHEMA = spi.final_validate_device_schema(
    "pcd8544", require_miso=False, require_mosi=True
)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])

    await display.register_display(var, config)
    await spi.register_spi_device(var, config)

    dc = await cg.gpio_pin_expression(config[CONF_DC_PIN])
    cg.add(var.set_dc_pin(dc))
    reset = await cg.gpio_pin_expression(config[CONF_RESET_PIN])
    cg.add(var.set_reset_pin(reset))

    cg.add(var.set_contrast(config[CONF_CONTRAST]))

    if CONF_LAMBDA in config:
        lambda_ = await cg.process_lambda(
            config[CONF_LAMBDA], [(display.DisplayRef, "it")], return_type=cg.void
        )
        cg.add(var.set_writer(lambda_))
