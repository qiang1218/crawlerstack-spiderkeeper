import { Button, styled } from "@mui/material";
import {
    EditButton,
    ShowButton,
    CreateButton,
    SelectColumnsButton,
    FilterButton,
} from "react-admin";

const defaultColor = "#2560ce";

export const SetButton = (color: string): any => {
    return {
        boxShadow: "none",
        textTransform: "none",
        fontSize: 12,
        padding: "5px 5px",
        lineHeight: 0.5,
        borderColor: color,
        fontFamily: [
            "-apple-system",
            "BlinkMacSystemFont",
            '"Segoe UI"',
            "Roboto",
            '"Helvetica Neue"',
            "Arial",
            "sans-serif",
            '"Apple Color Emoji"',
            '"Segoe UI Emoji"',
            '"Segoe UI Symbol"',
        ].join(","),
        "&:hover": {
            boxShadow: "rgba(66,66,66,0.35)",
        },
        "&:active": {
            boxShadow: "rgba(66,66,66,0.35)",
        },
        "&:focus": {
            boxShadow: "rgba(66,66,66,0.35)",
        },
    };
};

export const ShowOneButton = styled(ShowButton)(SetButton(defaultColor));

export const EditOneButton = styled(EditButton)(SetButton(defaultColor));

export const CreateItemButton = styled(CreateButton)(SetButton(defaultColor));

export const SelectColumnItem = styled(SelectColumnsButton)(
    SetButton(defaultColor)
);

export const FilterDropdownButton = styled(FilterButton)(
    SetButton(defaultColor)
);
export const StartButtonStyle = styled(Button)(SetButton("primary"));

export const RunButtonStyle = styled(Button)(SetButton("success"));

export const StopButtonStyle = styled(Button)(SetButton("error"));

export const PrimaryButtonStyle = styled(Button)(SetButton("secondary"));

export const UnpauseButtonStyle = styled(Button)(SetButton("info"));
