import { defaultTheme } from "react-admin";
import { RaThemeOptions } from "ra-ui-materialui";

export const darkTheme: RaThemeOptions = {
    palette: {
        primary: {
            main: "#87bdea",
        },
        secondary: {
            light: "#87bdea",
            main: "#5b95d2",
            dark: "#07416c",
            contrastText: "#fff",
        },
        info: {
            light: "#c4c4c4",
            main: "#9a9a9a",
            dark: "#808080",
            contrastText: "#fff",
        },
        background: {
            default: "#212121",
        },
        mode: "dark" as const, // Switching the dark mode on is a single property value change.
    },
    shape: {
        borderRadius: 10,
    },
    sidebar: {
        width: 200,
    },
    components: {
        ...defaultTheme.components,
        RaMenuItemLink: {
            styleOverrides: {
                root: {
                    borderLeft: "3px solid #000",
                    "&.RaMenuItemLink-active": {
                        borderLeft: "3px solid #90caf9",
                    },
                },
            },
        },
        MuiAppBar: {
            styleOverrides: {
                colorSecondary: {
                    color: "rgba(185,185,185,0.96)",
                    backgroundColor: "rgba(54,54,54,0.9)",
                },
            },
        },
        MuiLinearProgress: {
            styleOverrides: {
                colorPrimary: {
                    backgroundColor: "#4b4b4b",
                },
                barColorPrimary: {
                    backgroundColor: "#363636",
                },
            },
        },
        MuiTableRow: {
            styleOverrides: {
                root: {
                    "&:last-child td": { border: 0 },
                    backgroundColor: "rgba(44,44,44,0.73)",
                },
            },
        },
    },
};

export const lightTheme: RaThemeOptions = {
    palette: {
        primary: {
            main: "#4f3cc9",
        },
        secondary: {
            light: "#5f5fc4",
            main: "#49329b",
            dark: "#4a2a7c",
            contrastText: "#fff",
        },
        info: {
            light: "#0c0c0c",
            main: "#808080",
            dark: "#808080",
            contrastText: "#fff",
        },
        background: {
            default: "#fcfcfe",
        },
        mode: "light" as const,
    },
    shape: {
        borderRadius: 10,
    },
    sidebar: {
        width: 200,
    },
    components: {
        ...defaultTheme.components,
        RaMenuItemLink: {
            styleOverrides: {
                root: {
                    borderLeft: "3px solid #fff",
                    "&.RaMenuItemLink-active": {
                        borderLeft: "3px solid #4f3cc9",
                    },
                },
            },
        },
        MuiPaper: {
            styleOverrides: {
                elevation1: {
                    boxShadow: "none",
                },
                root: {
                    border: "1px solid #e0e0e3",
                    backgroundClip: "padding-box",
                },
            },
        },
        MuiAppBar: {
            styleOverrides: {
                colorSecondary: {
                    color: "#808080",
                    backgroundColor: "#fff",
                },
            },
        },
        MuiLinearProgress: {
            styleOverrides: {
                colorPrimary: {
                    backgroundColor: "#f5f5f5",
                },
                barColorPrimary: {
                    backgroundColor: "#d7d7d7",
                },
            },
        },
        MuiTableRow: {
            styleOverrides: {
                root: {
                    "&:last-child td": { border: 0 },
                },
            },
        },
    },
};
