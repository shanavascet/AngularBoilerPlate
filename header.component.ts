import { Component } from '@angular/core';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss']
})
export class HeaderComponent {
  appTitle = 'USBank - Campaign Generator - UAT';
  navItems = [
    { name: 'Home', link: '/dashboard' },
    { name: 'Dashboard', link: '/dashboard' },
    { name: 'Campaign', link: '/campaign-segmentation' },
    { name: 'Exclusion', link: '/loan-exclusion' },
    { name: 'Admin', link: '#' },
    { name: 'Contact TOS', link: '/contact-us' }
  ];
}
