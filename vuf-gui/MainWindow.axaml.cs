using Avalonia.Controls;

using System.Collections.Generic;

namespace vuf_gui
{
    public partial class MainWindow : Window
    {
        public MainWindow()
        {
            InitializeComponent();
        }

        public List<string> get_domains() { // c# binding to native code from vuf-lib
          List<string> domains = new List<string>();
          // TODO
          return domains;
        }
    }
}

