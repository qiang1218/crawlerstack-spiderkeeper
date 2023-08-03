import React from "react";

export const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));
