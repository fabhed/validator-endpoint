import { Space } from "antd";
import Stats from "../components/Stats";
import SWRRequestChart from "../components/charts/SWR/SWRRequestChart";

export default function Home() {
  return (
    <>
      <section style={{ marginBottom: 40 }}>
        <Space size={"large"} direction="vertical" style={{ display: "flex" }}>
          <Stats />
          <div>
            <SWRRequestChart />
          </div>
        </Space>
      </section>
    </>
  );
}
