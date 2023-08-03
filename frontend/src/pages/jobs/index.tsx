import JobList from "./JobsList";
import JobShow from "./JobShow";
import JobCreate from "./JobCreate";
import JobEdit from "./JobEdit";
import AssignmentRoundedIcon from "@mui/icons-material/AssignmentRounded";

export default {
    list: JobList,
    show: JobShow,
    create: JobCreate,
    edit: JobEdit,
    options: { label: "作业" },
    icon: AssignmentRoundedIcon,
};
