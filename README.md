# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default tseslint.config([
  globalIgnores(['dist-react']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...

      // Remove tseslint.configs.recommended and replace with this
      ...tseslint.configs.recommendedTypeChecked,
      // Alternatively, use this for stricter rules
      ...tseslint.configs.strictTypeChecked,
      // Optionally, add this for stylistic rules
      ...tseslint.configs.stylisticTypeChecked,

      // Other configs...
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default tseslint.config([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```


My Note:

Creation:

'npm create vite .' 
with React and textscript + SWC for build

'npm i'
to install node modules
'npm i electron-builder'
to use electron-builder to bundle up our application package.

'npm i --save-dev electron'
to install electron as a project devDependency. So, electron will not be installed as the project instead added as dependecy to the project specificaly as Dev dependency as it servers no purpous after package buid.

'npm run dev:react' (Configured in package.json as script)
to run the vite's dev environment in browser

'npm run build'
will build the react app and have the build files under 'dis-react' directory. To change the directory modify the build ourDir property in vite.config.ts

"main": "dist-electron/main.js", in the package.json tell the compiler that this is the starting point.
so the flow of app initilaize will be...
dist-electron/main.js creates a Browser window and load the index.html in that window, which is located in the <Program Files path> (in the case of windows) or <Applications path> (in the case of Linux & Mac) followed by the path of the project root -/dist-react/index.html. And in `index.html` which will have a div id-ed as `'root'`. and there is `src/ui/main.tsx` which will access the 'root' to create a dom that renders the component App which is `App.tsx`. The main.tsx will import the `React` and `ReactDOM` which is what making it as react application. This main.txs will also import the App component, its global style file `index.css`. 

```jsx
index.html
   └── <div id="root"></div>
main.txs
   └── ReactDOM.createRoot(document.getElementById('root'))
        └── render(<App />)
App.txs
   └── Contains all your actual UI and subcomponents
```

'npm run dev:electron' (Configured in package.json as script)
to run the app as an electron application.
Also make sure to rebase the root directory so subdirectries can be asseble and the application works in the eletron view. You can do that using 'base: './',' property configured in the vite.config.ts


"transpile:electron": "tsc -project src/electron/tsconfig.json" in the package.json will make the typescript conpiler to follow the configuration rules in tscofig.json. This command will compile the Typescript file into Javascript file and place it in dis-electron directory which is pointed as the entry point for our application.

Running the following based on the targeted platform will create the final application executable in the /dist directory.
npm run "dist:mac"
npm run "dist:win"
npm run "dist:linux"