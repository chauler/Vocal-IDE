import * as vscode from "vscode";
import { SetUpPython, StartServer } from "./setup-python";

export function activate(context: vscode.ExtensionContext) {
    SetUpPython();
    const disposable = vscode.commands.registerCommand("vocal-ide.startListening", () => {
        console.log("Starting Server");
        StartServer();
    });

    context.subscriptions.push(disposable);
}

export function deactivate() {}
