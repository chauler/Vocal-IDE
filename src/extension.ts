import * as vscode from "vscode";
import { SetUpPython, StartServer } from "./setup-python";

export function activate(context: vscode.ExtensionContext) {
    SetUpPython();
    const listeningCommand = vscode.commands.registerCommand("vocal-ide.startListening", () => {
        StartServer();
    });

    const insertTextCommand = vscode.commands.registerTextEditorCommand(
        "vocal-ide.insertText",
        (editor, editBuilder, input) => {
            editBuilder.insert(editor.selection.active, input);
        }
    );

    context.subscriptions.push(listeningCommand, insertTextCommand);
}

export function deactivate() {}
