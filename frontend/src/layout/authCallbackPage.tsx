import React, { useEffect } from "react";

const GitLabAuthCallbackPage = () => {
    useEffect(() => {
        // 获取认证完成后的 cookie
        const cookie = document.cookie; // 这里假设你的 cookie 名称为 'yourCookie'

        // 将 cookie 设置到浏览器中
        document.cookie = cookie;

        // 重定向回前端页面
        window.location.href = "/"; // 替换为你的前端页面路径
    }, []);

    return (
        <div>
            <p>Authenticating...</p>
        </div>
    );
};

export default GitLabAuthCallbackPage;
