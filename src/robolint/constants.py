"""Constants."""

import re

ASPIRATE_VVP96_STEP_ID = "453a73f0-be3e-0038-26c9-a717cfa4bcfb"
DISPENSE_VVP96_STEP_ID = "36d4aadc-134e-1706-4d47-6169e0b808cb"
MIX_VVP96_STEP_ID = "f3b7522f-7975-ee0a-362e-3b28132bca34"
MOVE_TO_PLATE_GRIPPER_STEP_ID = "b4456bd8-e178-8457-c202-c10ef4c671cb"
MOVE_TO_PLATE_STEP_ID = "4e41a614-7111-d08c-2f7e-6ba429023c36"
MULTI_DISPENSE_STEP = "979b25d3-8b26-8739-ce3a-f58aa12bb7ad"
COMMENT_STEPS_ID = "b373a8f8-2f99-4c10-aece-1b9a9273f5f1"
BEGIN_LOOP_STEP_ID = "565c02ef-0d8e-40bd-8906-4cc50e02fcb7"
TIP_EJECT_STEP_ID = "6ba4bf72-4115-3e40-0495-ad84983cf2e8"
TIP_LOAD_STEP_ID = "1d04aba5-dc42-e044-e57e-311ff530b30f"

DIRECTIVE_REGEX = re.compile(
    r"""    \#[ ]*robolint[ ]*\:            # initial pragma
            [ ]*disable[ ]*=[ ]*            # disable directive
            ([a-z\-]+([ ]*\,[ ]*[a-z\-]+)*) # names of rules to disable
    """,
    re.VERBOSE,
)
