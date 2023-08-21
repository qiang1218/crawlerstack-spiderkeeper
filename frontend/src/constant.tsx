import Chip from "@mui/material/Chip";
import DoneIcon from "@mui/icons-material/Done";
import PlayCircleFilledWhiteOutlinedIcon from "@mui/icons-material/PlayCircleFilledWhiteOutlined";
import StopCircleOutlinedIcon from "@mui/icons-material/StopCircleOutlined";
import PlaylistAddCheckOutlinedIcon from "@mui/icons-material/PlaylistAddCheckOutlined";
import LibraryAddOutlinedIcon from "@mui/icons-material/LibraryAddOutlined";
import PauseCircleOutlineOutlinedIcon from "@mui/icons-material/PauseCircleOutlineOutlined";
import DoNotDisturbOutlinedIcon from "@mui/icons-material/DoNotDisturbOutlined";
import RestartAltOutlinedIcon from "@mui/icons-material/RestartAltOutlined";
import ToggleOffOutlinedIcon from "@mui/icons-material/ToggleOffOutlined";
import ToggleOnRoundedIcon from "@mui/icons-material/ToggleOnRounded";
import UsbOffRoundedIcon from "@mui/icons-material/UsbOffRounded";
import UsbRoundedIcon from "@mui/icons-material/UsbRounded";
import RemoveCircleOutlineRoundedIcon from "@mui/icons-material/RemoveCircleOutlineRounded";
import Tooltip from "@mui/material/Tooltip";

export const Status = [
    {
        id: 1,
        name: (
            <Chip
                label="Created"
                size="small"
                color="primary"
                icon={<LibraryAddOutlinedIcon />}
            />
        ),
    },
    {
        id: 2,
        name: (
            <Chip
                label="Restarting"
                size="small"
                color="warning"
                icon={<RestartAltOutlinedIcon />}
            />
        ),
    },
    {
        id: 3,
        name: (
            <Chip
                label="Running"
                size="small"
                color="success"
                icon={<PlayCircleFilledWhiteOutlinedIcon />}
            />
        ),
    },
    {
        id: 4,
        name: (
            <Chip
                label="Paused"
                size="small"
                color="primary"
                icon={<PauseCircleOutlineOutlinedIcon />}
            />
        ),
    },
    {
        id: 5,
        name: (
            <Chip
                label="Exited"
                size="small"
                icon={<PlaylistAddCheckOutlinedIcon />}
            />
        ),
    },
    {
        id: 6,
        name: (
            <Chip
                label="Dead"
                size="small"
                color="error"
                icon={<DoNotDisturbOutlinedIcon />}
            />
        ),
    },
    {
        id: 7,
        name: (
            <Chip
                label="Online"
                size="small"
                color="secondary"
                icon={<UsbRoundedIcon />}
            />
        ),
    },
    {
        id: 8,
        name: (
            <Chip
                label="Offline"
                size="small"
                color="error"
                icon={<UsbOffRoundedIcon />}
            />
        ),
    },
    {
        id: 0,
        name: <Chip label="Finish" size="small" icon={<DoneIcon />} />,
    },
    {
        id: -1,
        name: (
            <Chip
                label="Stopped"
                size="small"
                color="error"
                icon={<StopCircleOutlinedIcon />}
            />
        ),
    },
    {
        id: -2,
        name: (
            <Chip
                label="Failure"
                size="small"
                color="error"
                icon={<StopCircleOutlinedIcon />}
            />
        ),
    },
    {
        id: true,
        name: (
            <Tooltip title="启用" arrow>
                <span>
                    <ToggleOnRoundedIcon
                        color="primary"
                        sx={{ fontSize: 28 }}
                    />
                </span>
            </Tooltip>
        ),
    },
    {
        id: false,
        name: (
            <Tooltip title="禁用" arrow>
                <span>
                    <ToggleOffOutlinedIcon
                        color="disabled"
                        sx={{ fontSize: 28 }}
                    />
                </span>
            </Tooltip>
        ),
    },
    {
        id: null,
        name: (
            <Chip
                label="null"
                size="small"
                icon={<RemoveCircleOutlineRoundedIcon sx={{ fontSize: 28 }} />}
            />
        ),
    },
];

export const StorageList = [
    { id: "mysql", name: "Mysql" },
    { id: "s3", name: "S3" },
    { id: "mongo", name: "MongoDB" },
    { id: "pulsar", name: "Pulsar" },
];
