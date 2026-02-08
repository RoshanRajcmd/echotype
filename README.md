# EchoType

A **vocalized typing practice desktop application** that helps users improve their typing skills through **audio prompts** and **real-time feedback**. Built using **Electron + React + TypeScript + Vite**, EchoType bridges modern web UI with native desktop capabilities.

## ⚙️ Source Code

> Single-repo Electron application

* **UI (React + Vite)**: Located under `src/ui`
* **Electron Main Process**: Located under `src/electron`

## 📚 Tech Stack and Packages

* Electron
* React
* TypeScript
* Vite
* SWC
* ESLint (Type-Checked Configuration)
* electron-builder

### Official Vite Plugins Used

* `@vitejs/plugin-react` – Babel-based Fast Refresh
* `@vitejs/plugin-react-swc` – SWC-based Fast Refresh (used for faster builds)

## 🎛️ Features

1. Vocalized typing prompts
2. Real-time typing feedback
3. Desktop application experience using Electron
4. Hot Module Reloading during development
5. Type-safe React architecture
6. Cross-platform build support (Windows, macOS, Linux)

## 🧑‍💻 Developer Setup

### 🏗️ Project Creation

```bash
npm create vite .
```

* Template: **React**
* Language: **TypeScript**
* Compiler: **SWC**

Install dependencies:

```bash
npm i
```

### ⚡ Electron Setup

Install Electron as a **dev dependency**:

```bash
npm i --save-dev electron
```

> Electron is only required during development and build time, not at runtime after packaging.

Install Electron Builder:

```bash
npm i electron-builder
```

Used to bundle the application into platform-specific executables.

---

### ▶️ Running the App

#### Run React (Browser)

```bash
npm run dev:react
```

* Runs Vite dev server in the browser
* Configured as a custom script in `package.json`

#### Build React

```bash
npm run build
```

* Outputs production files to `dist-react`
* To change output directory, modify `build.outDir` in `vite.config.ts`

#### Run Electron (Desktop)

```bash
npm run dev:electron
```

⚠️ **Important Vite Config**

To ensure assets resolve correctly in Electron:

```ts
base: './'
```

Configured in `vite.config.ts`.

---

### 🧠 Application Flow (Electron + React)

```txt
index.html
   └── <div id="root"></div>
main.tsx
   └── ReactDOM.createRoot(document.getElementById('root'))
        └── render(<App />)
App.tsx
   └── Contains all UI components
```

**Flow Explanation:**

1. Electron entry point is defined in `package.json`:

```json
"main": "dist-electron/main.js"
```

2. `dist-electron/main.js`:

   * Creates a browser window
   * Loads `dist-react/index.html`

3. `index.html`:

   * Contains `<div id="root"></div>`

4. `src/ui/main.tsx`:

   * Bootstraps React
   * Renders `<App />`
   * Imports global styles (`index.css`)

---

### 🔄 Electron TypeScript Transpilation

Script in `package.json`:

```json
"transpile:electron": "tsc -project src/electron/tsconfig.json"
```

* Compiles Electron TypeScript → JavaScript
* Outputs to `dist-electron`
* This directory is used as the Electron entry point

---

### 📦 Building Executables

Based on target platform, run:

```bash
npm run dist:mac
npm run dist:win
npm run dist:linux
```

* Final executables are generated in the `/dist` directory

---

## 🧹 ESLint Configuration

### Type-Checked ESLint Setup

```js
export default tseslint.config([
  globalIgnores(['dist-react']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      ...tseslint.configs.recommendedTypeChecked,
      ...tseslint.configs.strictTypeChecked,
      ...tseslint.configs.stylisticTypeChecked,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
    },
  },
])
```

### React-Specific ESLint Plugins (Optional)

```js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default tseslint.config([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      reactX.configs['recommended-typescript'],
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
    },
  },
])
```

---