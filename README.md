# A Debug Adapter for Debugging functions called by Custom Houdini UI Components

This adapter serves as a "middleman" between the Sublime Debugger plugin 
and a DAP implementation for python (debugpy) injected into Houdini.

It intercepts a few DAP requests to establish a connection between the debugger and Houdini, and 
otherwise forwards all communications between the debugger and debugpy normally.

## Installation

To install from repo,
- Open Sublime
- Install the "Debugger" plugin with Package Control if not done already
- In the "Preferences" menu, select "Browse Packages..."
- Clone this repository into the folder opened by Sublime
- Open the project you want to debug
    - If the debugger isn't open, select "Open" in the "Debugger" menu option
    - If it still doesn't open, ensure your project settings (Project -> Edit Project) are not empty, then try again
- Under the "Debugger" menu, select "Add or Select Configuration"
- Select "Add Configuration" from the suggestions
- There should be a "Houdini: Custom UI Debugging" option, click on it
- You should have your project settings automatically opened, edited with the configuration
- Save your project settings

## Use

- Go to Debugger -> Add or Select Configuration, and select "Houdini: Custom UI Debugging"
- Place breakpoints wherever needed
- Press play -- Nothing will seem to happen other than the pause button lighting 
- In Houdini, click on the relevant UI components to start debugging them

The Houdini UI Adapter should now be functional just by pressing play.

If it is your first time installing the adapter and Houdini is already open, make sure to restart Houdini first (a first-time setup is performed).

## Note

Currently only tested on Windows
