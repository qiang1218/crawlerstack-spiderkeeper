import { Card, Grid } from "@mui/material";
import Typography from "@mui/material/Typography";

const styles = {
    flex: { display: "flex" },
    flexColumn: { display: "flex", flexDirection: "column" },
    leftCol: { flex: 1, marginRight: "0.5em" },
    rightCol: { flex: 1, marginLeft: "0.5em" },
    singleCol: { marginTop: "1em", marginBottom: "1em" },
};

export const Dashboard = () => (
    <Card>
        <Grid container spacing={3} sx={{ margin: 2 }}>
            <Grid item xs={12}>
                <Typography variant="h3" gutterBottom>
                    数据采集平台 V4.0.1
                </Typography>
            </Grid>
            <Grid item xs={7}>
                <Typography variant="subtitle1" gutterBottom>
                    数据采集平台是一个提供调度功能和数据收集存储一体的任务平台，旨在减少爬虫开发和运维过程的复杂度，
                    让开发人员更着重于爬虫设计和业务逻辑开发，不需关注数据的存储和任务的调度，将极大的减少项目的开发周期，
                    提高开发效率。
                </Typography>
            </Grid>
            <Grid item xs={12}>
                <Typography variant="h4" gutterBottom>
                    使用指南
                </Typography>
                <Typography variant="h5" gutterBottom>
                    创建任务顺序依次是
                </Typography>
                <Typography variant="subtitle1" gutterBottom>
                    1、projects
                </Typography>
                <Typography variant="subtitle2" gutterBottom>
                    首先需要在项目页面点击 create 创建项目名称和基本表述。
                </Typography>
                <Typography variant="subtitle1" gutterBottom>
                    2、artifacts
                </Typography>
                <Typography variant="subtitle2" gutterBottom>
                    在归档页面创建归档配置。
                </Typography>
                <Typography variant="subtitle1" gutterBottom>
                    3、jobs
                </Typography>
                <Typography variant="subtitle2" gutterBottom>
                    在 作业 页面创建任务相关配置。
                </Typography>
            </Grid>
            <Grid item xs={12}>
                <Typography variant="h5" gutterBottom>
                    任务执行控制：
                </Typography>
                <Typography variant="subtitle2" gutterBottom>
                    在 作业 页面通过 start、stop、pause、unpause
                    四个按钮来控制任务的开启、停止、暂停与恢复，
                </Typography>
            </Grid>
            <Grid item xs={12}>
                <Typography variant="h5" gutterBottom>
                    任务消费控制：
                </Typography>
                <Typography variant="subtitle2" gutterBottom>
                    在 任务 页面通过 start、stop、terminate
                    三个按钮来控制任务消费状态，
                </Typography>
                <Typography variant="subtitle2" gutterBottom>
                    任务执行后会在任务页面更新其状态信息，并展示任务执行中产生的
                    log 日志
                </Typography>
            </Grid>
        </Grid>
    </Card>
);
