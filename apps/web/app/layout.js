import React from "react";

export default function RootLayout({ children }) {
  return React.createElement(
    "html",
    { lang: "zh-CN" },
    React.createElement("body", null, children)
  );
}
