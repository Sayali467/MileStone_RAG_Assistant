import { Component, ElementRef, ViewChild, AfterViewChecked, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { catchError } from 'rxjs/operators';
import { of } from 'rxjs';
import { environment } from '../environments/environment';

interface Message {
  role: 'user' | 'assistant' | 'disclaimer';
  text: string;
  citation?: string;
  citation_title?: string;
  last_updated?: string;
  is_refusal?: boolean;
}

export interface ChatHistory {
  id: string;
  title: string;
  messages: Message[];
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent implements AfterViewChecked, OnInit {
  get defaultMessages(): Message[] {
    return [
      {
        role: 'assistant',
        text: "Hello! I'm Genie. How can I assist you today?",
        is_refusal: true
      },
      {
        role: 'disclaimer',
        text: "Disclaimer: Genie's responses are for informational purposes only and do not constitute financial advice."
      }
    ];
  }

  messages: Message[] = [...this.defaultMessages];
  chatHistories: ChatHistory[] = [];
  activeChatId: string | null = null;
  
  userInput: string = '';
  isLoading: boolean = false;
  isSidebarCollapsed: boolean = true;
  isSidebarHovered: boolean = false;
  
  get isSidebarExpanded(): boolean {
    return !this.isSidebarCollapsed || this.isSidebarHovered;
  }
  
  isSchemesExpanded: boolean = false;
  isInputFocused: boolean = false;
  disclaimerTimeout: any;
  searchText: string = '';

  get hasStartedConversation(): boolean {
    return this.messages.some(msg => msg.role === 'user');
  }

  clearSearch() {
    this.searchText = '';
  }
  
  @ViewChild('chatContainer') private chatContainer!: ElementRef;
  @ViewChild('chatInput') private chatInput!: ElementRef<HTMLTextAreaElement>;

  constructor(private http: HttpClient, private sanitizer: DomSanitizer) {}

  ngOnInit() {
    this.scheduleDisclaimerRemoval();
  }

  scheduleDisclaimerRemoval() {
    if (this.disclaimerTimeout) {
      clearTimeout(this.disclaimerTimeout);
    }
    this.disclaimerTimeout = setTimeout(() => {
      this.messages = this.messages.filter(msg => msg.role !== 'disclaimer');
      this.syncActiveChat();
    }, 7000);
  }

  formatMessage(text: string): SafeHtml {
    if (!text) return '';
    // Replace markdown bold with HTML strong tags
    let formatted = text.replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold text-primary">$1</strong>');
    
    // Replace markdown lists (* or -) with tab spacing and a cyan bullet
    formatted = formatted.replace(/^[\*\-]\s+(.*)$/gm, '&nbsp;&nbsp;&nbsp;&nbsp;<span class="text-primary font-bold mr-2">&bull;</span>$1');
    
    return this.sanitizer.bypassSecurityTrustHtml(formatted);
  }

  syncActiveChat() {
    if (this.activeChatId) {
      const activeChat = this.chatHistories.find(c => c.id === this.activeChatId);
      if (activeChat) {
        activeChat.messages = [...this.messages];
      }
    }
  }

  ngAfterViewChecked() {
    this.scrollToBottom();
  }

  scrollToBottom(): void {
    try {
      if (this.chatContainer) {
        this.chatContainer.nativeElement.scrollTop = this.chatContainer.nativeElement.scrollHeight;
      }
    } catch(err) { }
  }

  toggleSidebar() {
    this.isSidebarCollapsed = !this.isSidebarCollapsed;
    this.isSidebarHovered = false; // Reset hover state when pinned/unpinned
  }

  expandSidebar() {
    this.isSidebarHovered = true;
  }

  collapseSidebar() {
    this.isSidebarHovered = false;
  }

  startNewChat() {
    this.activeChatId = null;
    this.messages = [...this.defaultMessages];
    this.userInput = '';
    this.scheduleDisclaimerRemoval();
  }

  loadChat(id: string) {
    const chat = this.chatHistories.find(c => c.id === id);
    if (chat) {
      this.activeChatId = id;
      this.messages = [...chat.messages];
    }
  }

  autoResize() {
    if (this.chatInput) {
      this.chatInput.nativeElement.style.height = 'auto';
      this.chatInput.nativeElement.style.height = (this.chatInput.nativeElement.scrollHeight) + 'px';
    }
  }

  onInputFocus() {
    this.isInputFocused = true;
  }

  onInputBlur() {
    this.isInputFocused = false;
  }

  handleQuery(query: string = this.userInput) {
    if (!query.trim()) return;
    
    if (!this.activeChatId) {
      const newId = Date.now().toString();
      this.activeChatId = newId;
      const newChat: ChatHistory = {
        id: newId,
        title: query,
        messages: [...this.messages]
      };
      this.chatHistories.unshift(newChat);
      if (this.chatHistories.length > 3) {
        this.chatHistories.pop();
      }
    }

    this.messages.push({ role: 'user', text: query });
    this.syncActiveChat();
    
    this.userInput = '';
    this.isLoading = true;
    
    // Reset textarea height
    if (this.chatInput) {
      this.chatInput.nativeElement.style.height = 'auto';
    }

    this.http.post<any>(environment.apiUrl, { query }).pipe(
      catchError(error => {
        console.error('Error fetching data', error);
        return of({ answer: 'Sorry, I encountered an error retrieving facts from the database.' });
      })
    ).subscribe(res => {
      this.isLoading = false;
      this.messages.push({
        role: 'assistant',
        text: res.answer,
        citation: res.citation,
        citation_title: res.citation_title,
        last_updated: res.last_updated,
        is_refusal: res.is_refusal
      });
      this.syncActiveChat();
    });
  }
}
