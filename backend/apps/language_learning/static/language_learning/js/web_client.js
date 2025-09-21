import { Component, useState, useSubEnv } from "@odoo/owl";
import { Navbar } from "./navbar";

export class WebClient extends Component {
    static template = "language_learning.WebClient";
    static components = { Navbar };
}
