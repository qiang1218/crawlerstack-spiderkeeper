import StorageCreate from "./StorageCreate";
import StoragesList from "./StorageList";
import StorageShow from "./StorageShow";
import StorageEdit from "./StorageEdit";
import BackupRoundedIcon from "@mui/icons-material/BackupRounded";

export default {
    list: StoragesList,
    create: StorageCreate,
    show: StorageShow,
    edit: StorageEdit,
    options: { label: "存储" },
    icon: BackupRoundedIcon,
};
