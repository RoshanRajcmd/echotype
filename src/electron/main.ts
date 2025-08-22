import { app, BrowserWindow } from 'electron';
import path from 'path';

// type test = string;

app.on('ready', () => {
    const mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
        },
        icon: path.join(__dirname, "../../favicon.png"), //App icon
    });

    // Load the React app
    mainWindow.loadFile(path.join(app.getAppPath(), '/dist-react/index.html'));
});