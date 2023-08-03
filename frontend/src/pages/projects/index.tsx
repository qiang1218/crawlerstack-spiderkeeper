import ProjectCreate from "./ProjectCreate";
import ProjectsList from "./ProjectsList";
import ProjectEdit from "./ProjectEdit";
import ProjectShow from "./ProjectShow";
import AccountTreeRoundedIcon from "@mui/icons-material/AccountTreeRounded";

export default {
    create: ProjectCreate,
    edit: ProjectEdit,
    list: ProjectsList,
    show: ProjectShow,
    options: { label: "项目" },
    icon: AccountTreeRoundedIcon,
};
