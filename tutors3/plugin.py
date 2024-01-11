import os
import pkg_resources
from glob import glob

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
        "STORAGE_BUCKET": "educateworkforce-private",
        "FILE_UPLOAD_BUCKET": "{{ S3_STORAGE_BUCKET }}",
        "PROFILE_IMAGE_BUCKET": "educateworkforce-public",
        "GRADE_BUCKET": "{{ S3_STORAGE_BUCKET }}",
        "COURSE_STRUCTURE_BUCKET": "{{ S3_STORAGE_BUCKET }}",
        "PROFILE_IMAGE_CUSTOM_DOMAIN": "d2xn5teicgwhnq.cloudfront.net",
        "PROFILE_IMAGE_MAX_AGE": "31536000",
        "ADDRESSING_STYLE": "auto",
        "SIGNATURE_VERSION": "s3v4",
        "CUSTOM_DOMAIN": "d38f8pc5t7fpx2.cloudfront.net",
    },
}


# Add the "templates" folder as a template root
hooks.Filters.ENV_TEMPLATE_ROOTS.add_item(
    pkg_resources.resource_filename("tutors3", "templates")
)
# Render the "build" and "apps" folders
hooks.Filters.ENV_TEMPLATE_TARGETS.add_items(
    [
        ("s3/build", "plugins"),
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
