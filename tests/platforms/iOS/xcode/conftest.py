import pytest

from ....utils import create_file, create_plist_file


@pytest.fixture
def first_app_generated(first_app_config, tmp_path):
    # Create the briefcase.toml file
    create_file(
        tmp_path
        / "base_path"
        / "build"
        / "first-app"
        / "ios"
        / "xcode"
        / "briefcase.toml",
        "\n".join(
            [
                "[paths]",
                'app_packages_path="app_packages"',
                'support_path="Support"',
                'info_plist_path="Info.plist"',
                "",
            ],
        ),
    )

    create_plist_file(
        tmp_path / "base_path/build/first-app/ios/xcode/Info.plist",
        {
            "MainModule": "first_app",
        },
    )

    # Create the support package VERSIONS file
    # with a deliberately weird min iOS version
    create_file(
        tmp_path / "base_path/build/first-app/ios/xcode/Support/VERSIONS",
        "\n".join(
            [
                "Python version: 3.10.15",
                "Build: b11",
                "Min iOS version: 14.2",
                "---------------------",
                "BZip2: 1.0.8-1",
                "libFFI: 3.4.6-1",
                "OpenSSL: 3.0.15-1",
                "XZ: 5.6.2-1",
                "",
            ]
        ),
    )
    # Create the package-config folders for each platform.
    # We don't need anything in them; they just need to exist.
    xcframework_path = (
        tmp_path / "base_path/build/first-app/ios/xcode/Support/Python.xcframework"
    )
    (xcframework_path / "ios-arm64/platform-config/arm64-iphoneos").mkdir(parents=True)
    (
        xcframework_path
        / "ios-arm64_x86_64-simulator/platform-config/arm64-iphonesimulator"
    ).mkdir(parents=True)
    (
        xcframework_path
        / "ios-arm64_x86_64-simulator/platform-config/x86_64-iphonesimulator"
    ).mkdir(parents=True)
    return first_app_config
