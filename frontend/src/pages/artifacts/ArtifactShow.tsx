import {
    DateField,
    ReferenceField,
    RichTextField,
    Show,
    SimpleShowLayout,
    TextField,
    useRecordContext,
} from "react-admin";
import { Grid, Divider, Box } from "@mui/material";
import ListItem from "@mui/material/ListItem";
import ListItemAvatar from "@mui/material/ListItemAvatar";
import Avatar from "@mui/material/Avatar";
import DisplaySettingsRoundedIcon from "@mui/icons-material/DisplaySettingsRounded";
import React from "react";
import { ShowTopToolbar } from "../ActionsToolbar";

const ArtifactTitle = () => {
    const record = useRecordContext();
    return <span>Artifact {record ? `"${record.name}"` : ""}</span>;
};

export const ArtifactShow = () => (
    <Box maxWidth="50em">
        <Show title={<ArtifactTitle />} actions={<ShowTopToolbar />}>
            <Grid container spacing={2} sx={{ margin: 2 }}>
                <ListItem>
                    <ListItemAvatar>
                        <Avatar>
                            <DisplaySettingsRoundedIcon />
                        </Avatar>
                    </ListItemAvatar>
                    <Grid item>
                        <SimpleShowLayout divider={<Divider flexItem />}>
                            <TextField
                                source="id"
                                label="ID"
                                fontSize="large"
                            />
                        </SimpleShowLayout>
                    </Grid>
                    <Grid item>
                        <SimpleShowLayout divider={<Divider flexItem />}>
                            <TextField
                                source="name"
                                label="归档名称"
                                fontSize="large"
                            />
                        </SimpleShowLayout>
                    </Grid>
                    <Grid item>
                        <SimpleShowLayout divider={<Divider flexItem />}>
                            <RichTextField
                                source="desc"
                                label="归档描述"
                                fontSize="large"
                            />
                        </SimpleShowLayout>
                    </Grid>
                </ListItem>
            </Grid>
            <Grid container>
                <Grid item xs={4}>
                    <SimpleShowLayout divider={<Divider flexItem />}>
                        <Grid item>
                            <SimpleShowLayout divider={<Divider flexItem />}>
                                <TextField
                                    source="image"
                                    label="镜像名称"
                                    fontSize="large"
                                />
                                <TextField
                                    source="tag"
                                    label="归档标签"
                                    fontSize="large"
                                />
                                <TextField
                                    source="version"
                                    label="镜像版本"
                                    fontSize={"large"}
                                />
                                <ReferenceField
                                    source="project_id"
                                    label="所属项目"
                                    reference="projects"
                                >
                                    <TextField source={"name"} />
                                </ReferenceField>
                            </SimpleShowLayout>
                        </Grid>
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

export default ArtifactShow;
