import {
    DateField,
    ReferenceField,
    SelectField,
    Show,
    SimpleShowLayout,
    TextField,
    useRecordContext,
    ChipField,
    TextFieldProps,
} from "react-admin";
import { Divider, Grid, Box } from "@mui/material";
import ListItemAvatar from "@mui/material/ListItemAvatar";
import Avatar from "@mui/material/Avatar";
import DisplaySettingsRoundedIcon from "@mui/icons-material/DisplaySettingsRounded";
import ListItem from "@mui/material/ListItem";
import { Status } from "../../constant";
import React from "react";
import { ShowTopToolbar } from "../ActionsToolbar";
import { makeStyles } from "@mui/styles";

const PageTitle = () => {
    const record: any = useRecordContext();
    return <span>{record ? `"${record.name}" 作业` : ""}</span>;
};

const useCodeBlockStyles = makeStyles({
    codeBlock: {
        fontFamily: "Courier New, monospace",
        borderRadius: "7px",
        fontSize: 14,
        backgroundColor: "#424242",
        padding: "0.5rem",
        margin: "0.5rem 0",
        whiteSpace: "pre-wrap",
        color: "#cccccc",
    },
});

interface CustomTextFieldProps extends TextFieldProps {
    source: string;
}

const CustomTextField: React.FC<CustomTextFieldProps> = ({ source }) => {
    const classes = useCodeBlockStyles();
    const record = useRecordContext();
    const value: string = record[source];
    if (!value) {
        return null;
    }
    const paragraphs: string[] = value.split(";"); // 使用分号分割字符串为段落数组
    const paragraphsContent = paragraphs.map((value, dix) => (
        <div>
            <div>
                {dix + 1} {value}
            </div>
        </div>
    ));
    return (
        <th align="left" className={classes.codeBlock}>
            {paragraphsContent}
        </th>
    );
};

export const JobShow: React.FC = () => {
    return (
        <Box maxWidth="65em">
            <Show actions={<ShowTopToolbar />} title={<PageTitle />}>
                <Grid item spacing={1} sx={{ margin: 2 }}>
                    <ListItem>
                        <ListItemAvatar>
                            <Avatar>
                                <DisplaySettingsRoundedIcon />
                            </Avatar>
                        </ListItemAvatar>
                        <Grid item xs={1}>
                            <SimpleShowLayout divider={<Divider flexItem />}>
                                <TextField source="id" fontSize="larger" />
                            </SimpleShowLayout>
                        </Grid>
                        <Grid container>
                            <SimpleShowLayout divider={<Divider flexItem />}>
                                <TextField source="name" fontSize="larger" />
                            </SimpleShowLayout>
                        </Grid>
                    </ListItem>
                </Grid>
                <Grid container spacing={2} sx={{ margin: 1 }}>
                    <Grid item xs={6}>
                        <Grid item xs={6}>
                            <SimpleShowLayout divider={<Divider flexItem />}>
                                <TextField
                                    source="executor_type"
                                    fontSize="large"
                                    label="执行器类型"
                                />
                                <TextField
                                    source="executor_selector"
                                    label="镜像版本"
                                    fontSize="large"
                                />
                                <ReferenceField
                                    source="artifact_id"
                                    reference="artifacts"
                                    label="归档名称"
                                >
                                    <TextField source="name" fontSize="large" />
                                </ReferenceField>
                                <ChipField
                                    source="trigger_expression"
                                    label="触发器表达式"
                                />
                                <ChipField
                                    source="cpu_limit"
                                    label="CPU限制 (millicores)"
                                />
                            </SimpleShowLayout>
                        </Grid>
                    </Grid>
                    <Grid item xs={6}>
                        <Grid item xs={6}>
                            <SimpleShowLayout divider={<Divider flexItem />}>
                                <SelectField
                                    source="enabled"
                                    label="Job状态"
                                    choices={Status}
                                    fontSize="larger"
                                />
                                <SelectField
                                    source="storage_enable"
                                    label="是否开启存储"
                                    choices={Status}
                                    fontSize="larger"
                                />
                                <ReferenceField
                                    source="storage_server_id"
                                    reference="storage_servers"
                                    label="存储模式"
                                >
                                    <TextField source="name" fontSize="large" />
                                </ReferenceField>
                                <SelectField
                                    source="pause"
                                    label="Pause状态"
                                    choices={Status}
                                    fontSize="larger"
                                />
                                <ChipField
                                    source="memory_limit"
                                    label="资源上限内存大小 (Mb)"
                                />
                            </SimpleShowLayout>
                        </Grid>
                    </Grid>
                </Grid>
                <Grid item sx={{ margin: 2 }}>
                    <Grid item>
                        <SimpleShowLayout divider={<Divider flexItem />}>
                            <TextField
                                source="cmdline"
                                fontSize="large"
                                label="任务运行参数"
                            />
                            <CustomTextField
                                source="environment"
                                label="任务运行环境变量参数"
                            />
                            <CustomTextField
                                source="volume"
                                label="任务运行挂载参数"
                            />
                            <DateField
                                id="outlined-basic"
                                source="create_time"
                                defaultChecked={false}
                                showTime
                                label="创建时间"
                            />
                            <DateField
                                source="update_time"
                                defaultChecked={false}
                                showTime
                                label="更新时间"
                            />
                        </SimpleShowLayout>
                    </Grid>
                </Grid>
            </Show>
        </Box>
    );
};

export default JobShow;
