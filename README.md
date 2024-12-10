# Voice Controlled IDE Extension README


## Milestone 1 (Oct. 23)
- Basic VSCode extension scaffolding
- Gets voice input and prints text to editor

## Milestone 2 (Nov. 4)
- Beginnings of Copilot and compiler implementations
- Very basic Copilot implementation: send POST requests to a Github endpoint for Copilot. Can't fully complete prompts yet, as no loop implemented, and can't send completion to VSCode.

## Milestone 3 (Nov. 18)
- Copilot implementation finished (Many parts to this)
- Added nice messages with embedded links to help guide the user through Github OAuth.
- Added GUI elements to VSCode. One button to act as a command shortcut, one visual indicator whether the system is listening.

## Milestone 4 (Dec. 9)
- (Under the hood) Migrate from pipes to websockets for easier message passing. Added a route handler and several routes: Copilot auth route, route for the ouput code, and route for logs intended for the user.
- Added a lexer and parser built using PLY.
- Implement a subset of Python using the lexer and parser.
