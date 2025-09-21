import { Component, useState, useSubEnv } from "@odoo/owl";
import { Navbar } from "./navbar.js";

export class WebClient extends Component {
    static template = "language_learning.WebClient";
    static components = { Navbar };
}
