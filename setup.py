from cx_Freeze import setup, Executable

target = Executable(
    script="Get Ducked.pyw",
    base="Win32GUI",
    icon="getducked.ico"
    )

setup(
    name="Get Ducked!",
    version="1.0",
    description="Get Ducked!",
    author="Mike Moon",
    executables=[target]
    )