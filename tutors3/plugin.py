import os
import pkg_resources
from glob import glob

import click
from tutor import hooks

from .__about__ import __version__


HERE = os.path.abspath(os.path.dirname(__file__))

config = {
    "defaults": {
        "VERSION": __version__,
        "HOST": "",
        "PORT": "",
        "REGION": "us-east-1",
        "USE_SSL": True,
        "STORAGE_BUCKET": "SET_ME_PLEASE",
        "FILE_UPLOAD_BUCKET": "{{ S3_STORAGE_BUCKET }}",
        "PROFILE_IMAGE_BUCKET": "educateworkforce-public",
        "GRADE_BUCKET": "{{ S3_STORAGE_BUCKET }}",
        "COURSE_STRUCTURE_BUCKET": "{{ S3_STORAGE_BUCKET }}",
        "PROFILE_IMAGE_CUSTOM_DOMAIN": "d2xn5teicgwhnq.cloudfront.net",
        "PROFILE_IMAGE_MAX_AGE": "31536000",
        "ADDRESSING_STYLE": "auto",
        "SIGNATURE_VERSION": "s3v4",
        "CUSTOM_DOMAIN": "SET_ME_PLEASE",
        # Staticfiles
        # -----------------------
        # Set to True to host static files on S3
        "ENABLE_S3_STATIC_FILES": True,
        # The bucket name to use for S3 static files
        "STATIC_FILES_BUCKET_NAME": "SET_ME_PLEASE",
        # Logrotate and s3cmd settings
        "UTILS_OUTPUT_DIRECTORY": "/openedx/utils",
        "UTILS_OUTPUT_DIRECTORY_SYNC_TO_S3": "/openedx/staticfiles",
         # AWS settings
        "AWS_CMD": "/usr/bin/aws",
        # AWS S3 settings
        "AWS_LOGFILE": "{{ S3_UTILS_OUTPUT_DIRECTORY }}/s3-staticfiles-sync.log",
        "AWS_STATICFILES_ACCESS_KEY_ID": "SET_ME_PLEASE",
        "AWS_STATICFILES_SECRET_KEY": "SET_ME_PLEASE",
        # S3cmd settings
        "UTILS_S3CMD": "/openedx/venv/bin/s3cmd",
        "UTILS_S3CMD_CONFIG": "/openedx/.s3cfg",
        "UTILS_S3CMD_BUCKET": "SET_ME_PLEASE",
        "UTILS_S3CMD_BUCKET_LOCATION": "SET_ME_PLEASE",
        "UITLS_S3CMD_CLOUDFRONT_HOST": "cloudfront.amazonaws.com",
        "UTILS_S3CMD_HOST_BASE": "s3.amazonaws.com",
        "UTILS_S3CMD_HOST_BUCKET": "%(bucket)s.s3.amazonaws.com",
        "UTILS_S3CMD_USE_HTTPS": "True",
    },
    "overrides": {
        # Setup error email handling
        # TBD: Using MS Teams for now.
        # ----------------------------------
        # # MS Teams Error Reporting
        # "MS_TEAMS_WEBHOOK_URL": "SET_ME_PLEASE",
        # "MS_TEAMS_ERROR_LINES": "4",
    }
}

########################################
# INITIALIZATION TASKS
########################################

# Using this instead of the MY_INIT_TASKS below to avoid the following error.
# jinja2.exceptions.TemplateNotFound
hooks.Filters.COMMANDS_INIT.add_item(
    (
        "lms",
        ("s3", "jobs", "lms", "init-staticfiles-s3"),
    )
)

# To add a custom initialization task, create a bash script template under:
# tutors3/templates/s3/jobs/init/
# and then add it to the MY_INIT_TASKS list. Each task is in the format:
# ("<service>", ("<path>", "<to>", "<script>", "<template>"))
MY_INIT_TASKS: list[tuple[str, tuple[str, ...]]] = [
    # For example, to add LMS initialization steps, you could add the script template at:
    # tutors3/templates/s3/jobs/init/lms.sh
    # And then add the line:
    # ("lms", ("s3", "jobs", "lms", "init-staticfiles-s3")),
]


# For each task added to MY_INIT_TASKS, we load the task template
# and add it to the COMMANDS_INIT filter, which tells Tutor to
# run it as part of the `init` job.
for service, template_path in MY_INIT_TASKS:
    full_path: str = pkg_resources.resource_filename(
        "tutors3", os.path.join("templates", *template_path)
    )
    with open(full_path, encoding="utf-8") as init_task_file:
        init_task: str = init_task_file.read()
    hooks.Filters.COMMANDS_INIT.add_item((service, init_task))


########################################
# TEMPLATE RENDERING
# (It is safe & recommended to leave
#  this section as-is :)
########################################

# Add the "templates" folder as a template root
hooks.Filters.ENV_TEMPLATE_ROOTS.add_item(
    pkg_resources.resource_filename("tutors3", "templates")
)
# Render the "build" and "apps" folders
hooks.Filters.ENV_TEMPLATE_TARGETS.add_items(
    [
        # ("s3/build", "plugins"),
        ("s3/build", "build/openedx/plugins"),
        ("s3/apps", "plugins"),
    ],
)
# Load patches from files
for path in glob(
    os.path.join(
        pkg_resources.resource_filename("tutors3", "patches"),
        "*",
    )
):
    with open(path, encoding="utf-8") as patch_file:
        hooks.Filters.ENV_PATCHES.add_item(
            (os.path.basename(path), patch_file.read())
        )
# Add configuration entries
hooks.Filters.CONFIG_DEFAULTS.add_items(
    [
        (f"S3_{key}", value)
        for key, value in config.get("defaults", {}).items()
    ]
)
hooks.Filters.CONFIG_UNIQUE.add_items(
    [
        (f"S3_{key}", value)
        for key, value in config.get("unique", {}).items()
    ]
)
hooks.Filters.CONFIG_OVERRIDES.add_items(
    list(config.get("overrides", {}).items())
)
