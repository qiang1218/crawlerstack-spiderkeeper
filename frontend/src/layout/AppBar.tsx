import * as React from "react";
import { AppBar, TitlePortal, UserMenu } from "react-admin";
import { Box, useMediaQuery, Theme } from "@mui/material";
import Login from "./login";
import LogOut from "./logout";

const CustomUserMenu = () => (
    <UserMenu>
        <Login />
        <LogOut />
    </UserMenu>
);

const CustomAppBar = () => {
    const isLargeEnough = useMediaQuery<Theme>((theme) =>
        theme.breakpoints.up("sm")
    );
    return (
        <AppBar color="secondary" elevation={2} userMenu={<CustomUserMenu />}>
            <TitlePortal />
            {isLargeEnough && <Box component="span" sx={{ flex: 1 }} />}
        </AppBar>
    );
};

export default CustomAppBar;
