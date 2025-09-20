/** @odoo-module **/

import { Component, useState, xml } from "@odoo/owl";
import { Navbar } from "../navbar";

export class WebClient extends Component {
  static template = xml`
    <div class="o_webclient">
      <Navbar />
      <div class="o_main_content">
        <div class="o_action_manager">
          <div class="notebook-main-content">
            <h1>Application Notebook</h1>
            <p>La navbar devrait apparaître ci-dessus</p>
          </div>
        </div>
      </div>
    </div>
  `;
  static components = { Navbar };

  setup() {
    this.state = useState({
      currentView: 'notes',
    });
  }
}