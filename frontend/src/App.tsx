import React from "react";
import { Admin, CustomRoutes, Resource } from "react-admin";
import JsonDataProvider from "./jsonDataProvider";
import { projects, artifacts, jobs, tasks, storages, Dashboard } from "./pages";
import executors from "./pages/executors";
import { Layout } from "./layout";
import Login from "./layout/login";
import { Route } from "react-router-dom";
import GitLabAuthCallbackPage from "./layout/authCallbackPage";
import { darkTheme, lightTheme } from "./layout/themes";

const apiUrl = "/api/v1";

const dataProvider = JsonDataProvider(apiUrl);

const App = () => {
    return (
        <Admin
            dataProvider={dataProvider}
            layout={Layout}
            dashboard={Dashboard}
            loginPage={Login}
            authCallbackPage={Dashboard}
            theme={lightTheme}
            darkTheme={darkTheme}
        >
            <Resource name="projects" {...projects} />
            <Resource name="artifacts" {...artifacts} />
            <Resource name="storage_servers" {...storages} />
            <Resource name="jobs" {...jobs} />
            <Resource name="tasks" {...tasks} />
            <Resource name="executors" {...executors} />
            <CustomRoutes>
                <Route
                    path="auth-callback-page"
                    element={<GitLabAuthCallbackPage />}
                />
            </CustomRoutes>
        </Admin>
    );
};

export default App;
