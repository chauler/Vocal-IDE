import { exec, ExecException, spawn, SpawnOptions } from "child_process";
import { rootDir } from "./util/rootdir";
import path from "path";
import * as vscode from "vscode";

//Called on extension startup. Executes a script that sets up a virtual python environment and installs necessary dependencies into it.
export function SetUpPython() {
    const scriptDir = path.join(rootDir, "voice-server");
    console.log(`"${path.join(scriptDir, "venv-setup.bat")}"`);
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
export function StartServer() {
    //Establish all the necessary paths to run the python script
    const interpretorPath = path.join(rootDir, "voice-server", "venv", "Scripts", "python.exe");
    const scriptPath = path.join(rootDir, "voice-server", "server.py");
    const options: SpawnOptions = {
        cwd: rootDir,
        env: { ...process.env },
        stdio: ["ignore", "pipe", "pipe"],
    };
    const server = spawn(`"${interpretorPath}"`, [scriptPath], options);

    //Currently, data from the python program is just piped to the extension.
    server.stdout?.on("data", (bytes) => {
        //Convert bytes to text and parse it. We currently distinguish control statements like error messages from actual output with the 'Data:' prefix.
        const inputString: string = bytes.toString("utf8");
        console.log(inputString);

        //This should probably be made more future-proof
        if (inputString.startsWith("Data:")) {
            vscode.commands.executeCommand("vocal-ide.insertText", inputString.replace("Data:", ""));
        }
    });

    server.stderr?.on("data", (data) => {
        console.log(data.toString("utf8"));
    });
    return server;
}
