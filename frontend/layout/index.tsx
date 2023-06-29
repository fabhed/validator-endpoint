import {
  FileTextOutlined,
  GithubOutlined,
  HomeOutlined,
  KeyOutlined,
  SettingOutlined,
} from "@ant-design/icons";
import { Layout, Menu, Typography, theme } from "antd";
import Link from "next/link";
import { useRouter } from "next/router";
import { useState } from "react";
import { github_repo_url, site_name } from "../constants";
import Navbar from "./Navbar";

const { Content, Footer, Sider } = Layout;
const { Title } = Typography;

const items = [
  {
    icon: <HomeOutlined style={{ marginRight: 8 }} />,
    label: <Link href="/">Dashboard</Link>,
    key: "/",
  },
  {
    icon: <KeyOutlined style={{ marginRight: 8 }} />,
    label: <Link href="/api-keys">API keys</Link>,
    key: "/api-keys",
  },
  {
    icon: <FileTextOutlined style={{ marginRight: 8 }} />,
    label: <Link href="/logs">Logs</Link>,
    key: "/logs",
  },
  {
    icon: <SettingOutlined style={{ marginRight: 8 }} />,
    label: <Link href="/configuration">Configuration</Link>,
    key: "/configuration",
  },
];

export default function RootLayout({ children }) {
  const router = useRouter();
  const {
    token: { colorBgContainer },
  } = theme.useToken();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <Layout hasSider>
      <Sider
        trigger={null}
        collapsible
        collapsed={collapsed}
        style={{
          minHeight: "100vh",
          height: "100%",
          position: "fixed",
        }}
      >
        <div
          className="text-center mt-2"
          style={{ textAlign: "center", marginTop: ".25rem" }}
        >
          {collapsed ? (
            <Title style={{ color: "white" }}>VE</Title>
          ) : (
            <Title style={{ color: "white" }}>{site_name}</Title>
          )}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          defaultSelectedKeys={router.pathname.split("/").slice(-1)}
        >
          {items.map((item) => (
            <Menu.Item key={item.key} icon={item.icon}>
              {item.label}
            </Menu.Item>
          ))}
        </Menu>
      </Sider>
      <Layout
        className="site-layout"
        style={{ marginLeft: collapsed ? 80 : 200, minHeight: "100vh" }}
      >
        <Navbar siderCollapsed={collapsed} setCollapsed={setCollapsed}></Navbar>
        <Content
          style={{
            margin: "24px 16px 0",
            overflow: "initial",
            flexGrow: 1,
          }}
        >
          {children}
        </Content>
        <Footer style={{ textAlign: "center" }}>
          {site_name}
          <a href={github_repo_url} target="_blank" rel="noopener noreferrer">
            <GithubOutlined style={{ marginLeft: 8 }} />
          </a>
        </Footer>
      </Layout>
    </Layout>
  );
}
