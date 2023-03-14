from core.module.windows import WindowsModule


if __name__ == '__main__':
    # Download and Execute Phishing Attachment - VBScript
    # m = WindowsModule("62385f03a0e69ed2274622cc", debug=False)
    # m.run()

    # Invoke Raw Powershell command
    # m = WindowsModule("628263ae9bad2dfa4b66d4c6")
    # m.run()

    # Scheduled Task - Persistance
    if len(sys.argv)>1:
        m = WindowsModule(sys.argv[1])
    else:
        m = WindowsModule("60f43effac529a1c1f25ebdc")
    m.run()
