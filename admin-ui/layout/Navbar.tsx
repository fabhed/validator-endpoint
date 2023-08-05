import { MenuFoldOutlined, MenuUnfoldOutlined } from "@ant-design/icons";
import { Button, Layout, theme } from "antd";
import "antd/dist/reset.css";
const { Header } = Layout;
import { Typography } from "antd";
import { relative } from "path";
const { Title } = Typography;

export default function Navbar({ siderCollapsed, setCollapsed }) {
  const {
    token: { colorBgContainer },
  } = theme.useToken();
  return (
    <Header
      style={{
        padding: 0,
        background: colorBgContainer,
        gap: "1rem",
      }}
    >
      <Button
        type="text"
        icon={siderCollapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
        onClick={() => setCollapsed(!siderCollapsed)}
        style={{
          fontSize: "16px",
          width: 64,
          height: 64,
        }}
      />

      <div
        style={{
          display: "flex",
          justifyContent: "center",
          width: "100%",
          height: "100%",
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            flexGrow: 1,
            maxWidth: "800px",
          }}
        ></div>
      </div>

      <div
        className="ml-auto pr-1"
        style={{
          marginLeft: "auto",
          display: "flex",
          alignItems: "center",
          marginRight: ".5rem",
          whiteSpace: "nowrap",
        }}
      ></div>
    </Header>
  );
}
