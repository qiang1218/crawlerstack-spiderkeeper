import {
    DateField,
    NumberField,
    ReferenceField,
    Show,
    SimpleShowLayout,
    TextField,
    useRecordContext,
    SelectField,
    TopToolbar,
} from "react-admin";
import { Divider, Grid, Box } from "@mui/material";
import React from "react";
import ListItem from "@mui/material/ListItem";
import ListItemAvatar from "@mui/material/ListItemAvatar";
import Avatar from "@mui/material/Avatar";
import DisplaySettingsRoundedIcon from "@mui/icons-material/DisplaySettingsRounded";
import { Status } from "../../constant";

const TaskTitle = () => {
    const record = useRecordContext();
    return <span>Task {record ? `"${record.name}"` : ""}</span>;
};

export const TaskShow = () => {
    return (
        <Box maxWidth="50em">
            <Show title={<TaskTitle />} actions={<TopToolbar></TopToolbar>}>
                <Grid container spacing={3} sx={{ margin: 2 }}>
                    <ListItem>
                        <ListItemAvatar>
                            <Avatar>
                                <DisplaySettingsRoundedIcon />
                            </Avatar>
                        </ListItemAvatar>
                        <Grid container xs={1}>
                            <SimpleShowLayout divider={<Divider flexItem />}>
                                <NumberField
                                    source="id"
                                    label={"Id"}
                                    fontSize={"large"}
                                />
                            </SimpleShowLayout>
                        </Grid>
                        <Grid container>
                            <SimpleShowLayout divider={<Divider flexItem />}>
                                <TextField
                                    source="name"
                                    label="任务名称"
                                    fontSize="large"
                                />
                            </SimpleShowLayout>
                        </Grid>
                    </ListItem>
                    <Grid container xs={5}>
                        <SimpleShowLayout divider={<Divider flexItem />}>
                            <SelectField
                                source="task_status"
                                label="任务状态"
                                choices={Status}
                                fontSize="large"
                            />
                            <SelectField
                                source="consume_status"
                                label="消费状态"
                                choices={Status}
                                fontSize="large"
                            />
                            <ReferenceField
                                source="job_id"
                                reference="jobs"
                                label="所属 Job"
                            >
                                <TextField source="name" fontSize="large" />
                            </ReferenceField>
                            <DateField
                                source="update_time"
                                showTime
                                label="Latest run"
                                fontSize="large"
                            />
                            <DateField
                                source="create_time"
                                showTime
                                label="创建时间"
                                fontSize="smaller"
                            />
                        </SimpleShowLayout>
                    </Grid>
                </Grid>
            </Show>
        </Box>
    );
};

export default TaskShow;
