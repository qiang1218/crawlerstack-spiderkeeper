import {
    DateField,
    Show,
    SimpleShowLayout,
    TextField,
    useRecordContext,
    useTranslate,
} from "react-admin";
import { Grid, Divider, Box } from "@mui/material";
import ListItem from "@mui/material/ListItem";
import ListItemAvatar from "@mui/material/ListItemAvatar";
import Avatar from "@mui/material/Avatar";
import DisplaySettingsRoundedIcon from "@mui/icons-material/DisplaySettingsRounded";
import ViewListRoundedIcon from "@mui/icons-material/ViewListRounded";
import { ShowTopToolbar } from "../ActionsToolbar";

const ProjectTitle = () => {
    const translate = useTranslate();
    const record = useRecordContext();
    return record ? (
        <span>
            {translate("resources.commands.title", {
                reference: record.reference,
            })}
        </span>
    ) : null;
};
export const ProjectShow = () => (
    <Box maxWidth="50em">
        <Show title={<ProjectTitle />} actions={<ShowTopToolbar />}>
            <Grid container spacing={2} sx={{ margin: 1 }}>
                <ListItem>
                    <ListItemAvatar>
                        <Avatar>
                            <DisplaySettingsRoundedIcon />
                        </Avatar>
                    </ListItemAvatar>
                    <Grid item xs={1}>
                        <SimpleShowLayout divider={<Divider flexItem />}>
                            <TextField
                                source="id"
                                fontSize="x-large"
                                label="Id"
                            />
                        </SimpleShowLayout>
                    </Grid>
                    <Grid item>
                        <SimpleShowLayout divider={<Divider flexItem />}>
                            <TextField
                                source="name"
                                fontSize="x-large"
                                label="项目名称"
                            />
                        </SimpleShowLayout>
                    </Grid>
                </ListItem>
            </Grid>
            <Grid container spacing={1} sx={{ margin: 1 }}>
                <ListItem>
                    <ListItemAvatar>
                        <Avatar>
                            <ViewListRoundedIcon />
                        </Avatar>
                    </ListItemAvatar>
                    <Grid item xs={3}>
                        <SimpleShowLayout divider={<Divider flexItem />}>
                            <TextField
                                source="desc"
                                fontSize="larger"
                                label="项目描述"
                            />
                        </SimpleShowLayout>
                    </Grid>
                </ListItem>
                <Grid item xs={3}>
                    <SimpleShowLayout divider={<Divider flexItem />}>
                        <DateField
                            source="create_time"
                            label="创建时间"
                            showTime
                        />
                        <DateField
                            source="update_time"
                            label="更新时间"
                            showTime
                        />
                    </SimpleShowLayout>
                </Grid>
            </Grid>
        </Show>
    </Box>
);

export default ProjectShow;
