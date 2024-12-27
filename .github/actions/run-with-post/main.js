const { spawn } = require("child_process");
const { appendFileSync } = require("fs");
const { EOL } = require("os");

function run(cmd) {
    const subprocess = spawn(cmd, { stdio: "inherit", shell: true });
    subprocess.on("exit", (exitCode) => {
        process.exitCode = exitCode;
    });
}

// Export environment variables
for (const key in process.env) {
    if (key.indexOf("INPUT_") >= 0) {
        process.env[key.replace("INPUT_", "")] = process.env[key]
    }
}

if ( process.env[`STATE_POST`] !== undefined ) {
    // Run post scripts.
    run(process.env["INPUT_POST"]);
} else {
    // Run main scripts.
    appendFileSync(process.env.GITHUB_STATE, `POST=true${EOL}`);
    run(process.env["INPUT_RUN"]);
}
