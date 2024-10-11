import { exec, ExecException, spawn, SpawnOptions } from "child_process";
import { rootDir } from "./util/rootdir";
import path from "path";

export function SetUpPython() {
    const scriptDir = path.join(rootDir, "voice-server");
    exec(path.join(scriptDir, "venv-setup.bat"), (error: ExecException | null, stdout: string, stderr: string) => {
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
    });
}

export function StartServer() {
    const interpretorPath = path.join(rootDir, "voice-server", "venv", "Scripts", "python.exe");
    const scriptPath = path.join(rootDir, "voice-server", "server.py");
    const options: SpawnOptions = {
        cwd: rootDir,
        env: { ...process.env },
        stdio: ["ignore", "pipe", "pipe"],
    };
    const server = spawn(interpretorPath, [scriptPath], options);
    server.stdout?.on("data", (data) => {
        console.log(data.toString("utf8"));
    });
    server.stderr?.on("data", (data) => {
        console.log(data.toString("utf8"));
    });
    return server;
}
