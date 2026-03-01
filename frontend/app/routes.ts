import { type RouteConfig, route, layout } from "@react-router/dev/routes";


export default [

  // All routes inside this 'layout' will render inside the AuthLayout's <Outlet />
    layout("layouts/DashboardLayout.tsx", [
        route("chat", "routes/GreatRoute.tsx"),
    ]),
    
    layout("layouts/AuthLayout.tsx", [
        route("login", "routes/LoginRoute.tsx"),
        route("register", "routes/RegisterRoute.tsx"),
    ]),

    route("logout", "routes/LogoutRoute.tsx"),

] satisfies RouteConfig;