# DraftShieldSpeed.py
# Cura 5.13 post-processing script
#
# Separates Draft Shield speed from the shared skirt/brim speed.
#
# Cura emits the draft shield as TYPE:SKIRT after layer 0.  This script leaves
# layer 0 untouched, changes only extrusion moves inside later TYPE:SKIRT
# sections, and restores the previous print feed rate after each section.

from ..Script import Script
import json
import re


class DraftShieldSpeed(Script):
    def getSettingDataString(self):
        return json.dumps({
            "name": "Draft Shield Speed",
            "key": "DraftShieldSpeed",
            "metadata": {},
            "version": 2,
            "settings": {
                "speed_source": {
                    "label": "Draft Shield Speed Source",
                    "description": (
                        "Use Cura's Print Speed for the draft shield, or set "
                        "a custom draft-shield speed."
                    ),
                    "type": "enum",
                    "options": {
                        "print": "Print Speed",
                        "custom": "Custom"
                    },
                    "default_value": "print"
                },
                "draft_shield_speed": {
                    "label": "Draft Shield Speed",
                    "description": "Custom draft shield speed in mm/s.",
                    "type": "float",
                    "unit": "mm/s",
                    "default_value": 60.0,
                    "minimum_value": 1.0,
                    "enabled": "speed_source == \"custom\""
                }
            }
        })

    def execute(self, data):
        source = self.getSettingValueByKey("speed_source")

        if source == "custom":
            target_speed = float(
                self.getSettingValueByKey("draft_shield_speed")
            )
        else:
            # Cura exposes machine/profile values to post-processing scripts.
            # `speed_print` is in mm/s.
            target_speed = float(
                self._application.getGlobalContainerStack()
                .getProperty("speed_print", "value")
            )

        target_f = target_speed * 60.0

        layer = -1
        in_draft_shield = False
        last_print_f = None
        restore_f = None

        layer_re = re.compile(r"^;LAYER:(-?\d+)")
        f_re = re.compile(r"(?:^|\s)F(-?\d+(?:\.\d+)?)")

        out = []

        for block in data:
            lines = block.splitlines(True)
            new_lines = []

            for line in lines:
                stripped = line.strip()

                m_layer = layer_re.match(stripped)
                if m_layer:
                    layer = int(m_layer.group(1))

                if stripped.startswith(";TYPE:"):
                    new_type_is_skirt = (
                        stripped == ";TYPE:SKIRT" and layer >= 1
                    )

                    if in_draft_shield and not new_type_is_skirt:
                        in_draft_shield = False

                    if new_type_is_skirt and not in_draft_shield:
                        in_draft_shield = True
                        restore_f = last_print_f

                # Track feed rates used by actual extrusion moves outside the
                # draft-shield section. Travels/retractions are deliberately
                # ignored so they remain untouched.
                is_g1 = stripped.startswith("G1 ")
                has_e = is_g1 and (" E" in (" " + stripped))
                has_xy = is_g1 and (
                    " X" in (" " + stripped) or " Y" in (" " + stripped)
                )
                is_print_move = has_e and has_xy

                if is_print_move:
                    m_f = f_re.search(stripped)

                    if in_draft_shield:
                        if m_f:
                            line = re.sub(
                                r"(?<!\S)F-?\d+(?:\.\d+)?",
                                "F{:.3f}".format(target_f).rstrip("0").rstrip("."),
                                line,
                                count=1,
                            )
                        else:
                            # Cura normally emits an F at the beginning of the
                            # section. Add one if it did not.
                            newline = "\n" if line.endswith("\n") else ""
                            body = line[:-1] if newline else line
                            line = "{} F{}{}".format(
                                body,
                                "{:.3f}".format(target_f).rstrip("0").rstrip("."),
                                newline,
                            )
                    else:
                        if m_f:
                            last_print_f = float(m_f.group(1))

                # When leaving TYPE:SKIRT, restore the feed rate on the first
                # subsequent extrusion move if Cura did not already provide F.
                if (
                    not in_draft_shield
                    and restore_f is not None
                    and is_print_move
                ):
                    if f_re.search(line) is None:
                        newline = "\n" if line.endswith("\n") else ""
                        body = line[:-1] if newline else line
                        line = "{} F{}{}".format(
                            body,
                            "{:.3f}".format(restore_f).rstrip("0").rstrip("."),
                            newline,
                        )
                    restore_f = None

                new_lines.append(line)

            out.append("".join(new_lines))

        return out
