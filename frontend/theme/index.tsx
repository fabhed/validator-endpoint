import React from "react";
import { ConfigProvider } from "antd";
import { blue } from "@ant-design/colors";

const withTheme = (node: JSX.Element) => (
  <ConfigProvider
    theme={{
      token: {
        colorPrimary: "#000",
        controlItemBgActive: blue[0],
        borderRadius: 16,
      },
    }}
  >
    {node}
  </ConfigProvider>
);

export default withTheme;
