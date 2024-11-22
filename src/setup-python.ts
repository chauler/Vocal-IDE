import { exec, ExecException, spawn, SpawnOptions } from "child_process";
import { isString, isValidObject, rootDir } from "./util/util";
import WebSocket, { WebSocketServer } from "ws";
import path from "path";
import * as util from "util";
import * as vscode from "vscode";

//Called on extension startup. Executes a script that sets up a virtual python environment and installs necessary dependencies into it.
export function SetUpPython() {
    const scriptDir = path.join(rootDir, "voice-server");
    exec(
        `"${path.join(scriptDir, "venv-setup.bat")}"`,
        (error: ExecException | null, stdout: string, stderr: string) => {
            if (error) {
                console.error(`exec error: ${error}`);
                return;
            }

            if (stdout.length) {
                console.log(`stdout: ${stdout}`);
            }

            if (stderr.length) {
                console.error(`stderr: ${stderr}`);
            }
        }
    );
}

//Runs the main python script for listening.
export function StartServer(mode: "COPILOT" | "COMPILER" | "OTHER" = "OTHER") {
    const wss = new WebSocketServer({ port: 8080 });

    const routeHandlers: Record<string, (arg0: Record<string, unknown>) => void> = {
        auth: (message) => {
            vscode.window.showInformationMessage(
                new vscode.MarkdownString(`Click this [Link](${message.uri}) and enter the code ${message.code}`).value,
                "Dismiss"
            );
        },
        data: (message) => {
            console.log(`data: ${util.inspect(message)}`);
        },
        message: (message) => {
            if (typeof message.message === "string") {
                vscode.window.showInformationMessage(message.message);
            }
        },
    };

    wss.on("connection", function connection(ws, req) {
        ws.on("error", (err) => console.log(err));

        ws.on("message", function incoming(message) {
            const parsedMessage: unknown = JSON.parse(message.toString());
            if (isValidObject(parsedMessage) && isString(parsedMessage.route) && isValidObject(parsedMessage.data)) {
                parsedMessage.route;
                routeHandlers[parsedMessage.route](parsedMessage.data);
            } else {
                console.error("Invalid message received from websocket");
            }
        });
    });

    //Establish all the necessary paths to run the python script
    const interpretorPath = path.join(rootDir, "voice-server", "venv", "Scripts", "python.exe");
    const scriptPath = path.join(rootDir, "voice-server", "main.py");
    const options: SpawnOptions = {
        cwd: rootDir,
        env: { ...process.env, SERVER_PORT: "8080", MODE: mode },
        stdio: ["ignore", "pipe", "pipe"],
    };

    vscode.commands.executeCommand("setContext", "vocal-ide.isListening", true);
    const server = spawn(`${interpretorPath}`, [scriptPath], options);

    server.stdout?.on("data", (bytes) => {
        console.log(`stdout: ${bytes.toString("utf8")}`);
    });

    server.stderr?.on("data", (bytes) => {
        console.error(`stderr: ${bytes.toString("utf8")}`);
    });

    server.on("close", (code, signal) => {
        vscode.commands.executeCommand("setContext", "vocal-ide.isListening", false);
    });
    return server;
}
