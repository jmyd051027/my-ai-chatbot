
import { writeFileSync } from "node:fs";

const apiBaseUrl = process.env.API_BASE_URL;

if (!apiBaseUrl) {
    throw new Error("API_BASE_URL 환경변수가 설정되지 않았습니다.");
}

const config = {
    API_BASE_URL: apiBaseUrl.replace(/\/+$/, "")
};

writeFileSync(
    "config.js",
    `window.APP_CONFIG = ${JSON.stringify(config, null, 2)};\n`,
    "utf8"
);

console.log("API configuration generated successfully.");
