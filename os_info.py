import platform

def get_os_info():
    os_type = platform.system().lower()

    if os_type == "linux":
        import distro
        return {
            "type": "Linux",
            "name": distro.name(),
            "version": distro.version(),
            "id": distro.id(),
        }
    elif os_type == "windows":
        return {
            "type": "Windows",
            "version": platform.version(),
            "release": platform.release(),
        }
    elif os_type == "darwin":
        return {
            "type": "macOS",
            "version": platform.mac_ver()[0],
        }
    else:
        return {
            "type": os_type.capitalize(),
            "version": platform.version(),
        }