-- gptars v3.0 - Microphone and Camera Permission Request
-- This script triggers macOS permission dialogs for microphone and camera access
-- Run this after installation to ensure TARS can access audio/video input

on run
	display dialog "gptars v3.0 needs access to your microphone and camera for voice and vision features.

Click OK to grant permissions when prompted by macOS." buttons {"OK"} default button "OK" with icon note with title "gptars Permission Request"
	
	try
		-- Request microphone access by trying to use it
		-- This will trigger the macOS permission dialog
		do shell script "echo 'Testing microphone access...'"
		
		-- Note: The actual permission request happens when the app first tries to use the microphone
		-- macOS will show a system dialog automatically
		
		display dialog "Please check System Preferences > Security & Privacy > Privacy:

1. Microphone - Enable for Terminal (or your Python app)
2. Camera - Enable for Terminal (or your Python app)

These permissions are required for TARS to function properly." buttons {"Open System Preferences", "Done"} default button "Done" with icon note with title "Permission Setup"
		
		-- If user wants to open System Preferences
		set userChoice to button returned of result
		if userChoice is "Open System Preferences" then
			do shell script "open 'x-apple.systempreferences:com.apple.preference.security?Privacy_Microphone'"
			delay 2
			do shell script "open 'x-apple.systempreferences:com.apple.preference.security?Privacy_Camera'"
		end if
		
	on error errMsg
		display dialog "Error requesting permissions: " & errMsg buttons {"OK"} default button "OK" with icon stop
	end try
end run
